import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.ImageType;
import org.apache.pdfbox.rendering.PDFRenderer;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class PdfToBlackAndWhitePng {

    public static void main(String[] args) {
        String pdfPath = "path/to/your/document.pdf";
        String outputPath = "path/to/output/image.png";
        int dpi = 152;
        float threshold = 0.5f; // Adjust this value to control the threshold (0.0 to 1.0)

        try {
            PDDocument document = PDDocument.load(new File(pdfPath));
            PDFRenderer pdfRenderer = new PDFRenderer(document);

            // Render the first page to an image
            BufferedImage coloredImage = pdfRenderer.renderImageWithDPI(0, dpi, ImageType.RGB);

            // Convert to black and white with threshold
            BufferedImage blackAndWhiteImage = convertToBlackAndWhite(coloredImage, threshold);

            // Save the black and white image as PNG
            ImageIO.write(blackAndWhiteImage, "png", new File(outputPath));

            document.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static BufferedImage convertToBlackAndWhite(BufferedImage coloredImage, float threshold) {
        BufferedImage bwImage = new BufferedImage(
                coloredImage.getWidth(), 
                coloredImage.getHeight(), 
                BufferedImage.TYPE_BYTE_BINARY);
        
        Graphics2D graphics = bwImage.createGraphics();
        graphics.drawImage(coloredImage, 0, 0, null);
        graphics.dispose();

        for (int x = 0; x < coloredImage.getWidth(); x++) {
            for (int y = 0; y < coloredImage.getHeight(); y++) {
                int rgb = coloredImage.getRGB(x, y);
                int gray = (int) (0.2126 * ((rgb >> 16) & 0xFF) + 0.7152 * ((rgb >> 8) & 0xFF) + 0.0722 * (rgb & 0xFF));
                int bw = gray < (threshold * 255) ? 0 : 255;
                int newRgb = (bw << 16) | (bw << 8) | bw;
                bwImage.setRGB(x, y, newRgb);
            }
        }
        return bwImage;
    }
}
