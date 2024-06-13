package com.hcl.pdf2image;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;

import org.apache.batik.transcoder.TranscoderException;
import org.apache.batik.transcoder.TranscoderInput;
import org.apache.batik.transcoder.TranscoderOutput;
import org.apache.batik.transcoder.image.PNGTranscoder;

public class App {
    public static void main(String[] args) throws IOException, TranscoderException {
        // Input SVG file
        File svgFile = new File("input.svg");

        // Output PNG file
        File pngFile = new File("output.png");

        // Create a PNG transcoder
        PNGTranscoder transcoder = new PNGTranscoder();

        // Set the transcoding hints
        transcoder.addTranscodingHint(PNGTranscoder.KEY_BACKGROUND_COLOR, java.awt.Color.WHITE);
//        transcoder.addTranscodingHint(PNGTranscoder.KEY_PIXEL_UNIT_TO_MILLIMETER, (float)(25.4 / 152));  // 152 DPI
        transcoder.addTranscodingHint(PNGTranscoder.KEY_PIXEL_UNIT_TO_MILLIMETER, (float)(25.4/ 152));  // 152 DPI
//        transcoder.addTranscodingHint(PNGTranscoder.KEY_FORCE_TRANSPARENT_WHITE, false);
        transcoder.addTranscodingHint(PNGTranscoder.KEY_INDEXED, 1);

        // Create the transcoder input
        String svgURI = svgFile.toURI().toString();
        TranscoderInput input = new TranscoderInput(svgURI);

        // Create the transcoder output
        OutputStream outputStream = new FileOutputStream(pngFile);
        TranscoderOutput output = new TranscoderOutput(outputStream);

        // Perform the transcoding
        transcoder.transcode(input, output);

        // Flush and close the output stream
        outputStream.flush();
        outputStream.close();

        System.out.println("Conversion completed: " + pngFile.getAbsolutePath());
    }
}
