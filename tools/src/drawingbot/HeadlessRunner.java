package drawingbot;

import drawingbot.api.IGeometryFilter;
import drawingbot.files.ExportTask;
import drawingbot.files.DrawingExportHandler;
import drawingbot.registry.MasterRegistry;
import drawingbot.registry.Register;
import javafx.application.Platform;

import java.io.File;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Converts an image into plotter-ready vectors using DrawingBotV3 without the GUI.
 * Usage: HeadlessRunner <image> <outputDir> [PFM name] [svg,gcode,pdf,png]
 */
public class HeadlessRunner {

    static boolean plotDone() {
        // PFMTask sets the finished drawing and clears the active task when done
        return DrawingBotV3.project().activeTask.get() == null && DrawingBotV3.taskManager().getCurrentDrawing() != null;
    }

    static long lastSize = -1; static int stable = 0;
    static boolean fileStable(File f) {
        long sz = f.exists() ? f.length() : -1;
        stable = (sz > 0 && sz == lastSize) ? stable + 1 : 0;
        lastSize = sz;
        return stable >= 3;
    }

    static void runFx(Runnable r) throws InterruptedException {
        CountDownLatch l = new CountDownLatch(1);
        Platform.runLater(() -> { try { r.run(); } finally { l.countDown(); } });
        l.await();
    }

    static void waitFor(String what, java.util.function.BooleanSupplier cond) throws Exception {
        if (!waitFor(what, cond, 30 * 60)) { System.err.println("[runner] Timed out waiting for " + what); System.exit(3); }
    }

    static boolean waitFor(String what, java.util.function.BooleanSupplier cond, int seconds) throws Exception {
        int ticks = 0;
        long deadline = System.currentTimeMillis() + TimeUnit.SECONDS.toMillis(seconds);
        while (true) {
            AtomicBoolean ok = new AtomicBoolean();
            runFx(() -> ok.set(cond.getAsBoolean()));
            if (ok.get()) return true;
            if (System.currentTimeMillis() > deadline) return false;
            Thread.sleep(500);
            if (++ticks % 20 == 0) System.out.println("[runner] waiting for " + what + "...");
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: HeadlessRunner <image> <outputDir> [\"Sketch Lines PFM\"|\"Sketch Squares PFM\"|\"Spiral PFM\"] [svg,gcode,pdf,png]");
            System.exit(1);
        }
        File image = new File(args[0]).getAbsoluteFile();
        File outDir = new File(args[1]).getAbsoluteFile();
        String pfmName = args.length > 2 ? args[2] : "Sketch Lines PFM";
        String formats = args.length > 3 ? args[3] : "svg,gcode";
        String settings = args.length > 4 ? args[4] : "";   // "Line Density=40;Plotting Resolution=0.5"
        outDir.mkdirs();
        String base = image.getName().replaceFirst("\\.[^.]+$", "");

        FXApplication.isUnitTesting = true;
        Thread fx = new Thread(() -> Launcher.main(new String[0]));
        fx.setDaemon(true);
        fx.start();
        while (true) {
            if (FXApplication.isLoaded.get()) break;
            if (!fx.isAlive() && !FXApplication.isLoaded.get()) { Thread.sleep(2000); if (!FXApplication.isLoaded.get()) { System.err.println("[runner] App failed to start"); System.exit(4);} }
            Thread.sleep(200);
        }

        Thread.sleep(2000); // let the startup project settle
        var factory = MasterRegistry.INSTANCE.getPFMFactory(pfmName);
        if (factory == null) { System.err.println("[runner] Unknown PFM: " + pfmName); System.exit(2); }
        boolean ok = false;
        for (int attempt = 1; attempt <= 5 && !ok; attempt++) {
            runFx(() -> {
                DrawingBotV3.project().getPFMSettings().setPFMFactory(factory);
                DrawingBotV3.INSTANCE.openFile(DrawingBotV3.context(), image, false, false);
            });
            ok = waitFor("image load", () -> DrawingBotV3.project().openImage.get() != null, 20);
            if (!ok) System.out.println("[runner] Image not loaded yet, retrying (" + attempt + ")...");
        }
        if (!ok) { System.err.println("[runner] Could not load image"); System.exit(3); }
        if (!settings.isBlank()) {
            runFx(() -> {
                for (String kv : settings.split(";")) {
                    String[] p = kv.split("=", 2);
                    if (p.length != 2) continue;
                    boolean found = false;
                    for (var st : DrawingBotV3.project().getPFMSettings().getSettings()) {
                        if (st.getKey().equalsIgnoreCase(p[0].trim())) {
                            st.setValueFromString(p[1].trim());
                            System.out.println("[runner] " + st.getKey() + " = " + st.getValueAsString());
                            found = true;
                        }
                    }
                    if (!found) System.out.println("[runner] Setting not found: " + p[0]);
                }
            });
        }
        System.out.println("[runner] Image loaded, plotting with " + pfmName + "...");

        runFx(() -> DrawingBotV3.INSTANCE.startPlotting(DrawingBotV3.context()));
        Thread.sleep(1000);
        waitFor("plotting", () -> plotDone());
        System.out.println("[runner] Plot finished, exporting " + formats + "...");

        for (String f : formats.split(",")) {
            DrawingExportHandler h; String ext;
            switch (f.trim()) {
                case "svg" -> { h = Register.EXPORT_SVG; ext = ".svg"; }
                case "gcode" -> { h = Register.EXPORT_GCODE; ext = ".gcode"; }
                case "pdf" -> { h = Register.EXPORT_PDF; ext = ".pdf"; }
                case "png" -> { h = Register.EXPORT_IMAGE; ext = ".png"; }
                default -> { System.err.println("[runner] Unknown format " + f); continue; }
            }
            File target = new File(outDir, base + ext);
            runFx(() -> DrawingBotV3.INSTANCE.createExportTask(h, ExportTask.Mode.PER_DRAWING, DrawingBotV3.taskManager().getCurrentDrawing(), IGeometryFilter.DEFAULT_FILTER, ext, target, false));
            Thread.sleep(500);
            waitFor("export " + f, () -> fileStable(target));
            System.out.println("[runner] Wrote " + target);
        }
        System.out.println("[runner] Done -> " + outDir);
        System.exit(0);
    }
}
