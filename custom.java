import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;
import javax.imageio.ImageIO;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;

public class PDFToGrayscaleBWImage {

    public static void main(String[] args) throws IOException {
        // Replace "your_pdf_file.pdf" with the path to your PDF file
        String pdfFilePath = "your_pdf_file.pdf";
        // Replace "output.png" with your desired output file name
        String outputFilePath = "output.png";

        // Set DPI for the output image
        int dpi = 152;

        // PDF to grayscale image
        BufferedImage grayscaleImage = pdfToGrayscaleImage(pdfFilePath, dpi);

        // Convert grayscale image to black and white with threshold adjustment
        BufferedImage blackAndWhiteImage = grayscaleToBlackAndWhite(grayscaleImage);

        // Write the final image to PNG file
        writeImageToFile(blackAndWhiteImage, outputFilePath, "png");
    }

    private static BufferedImage pdfToGrayscaleImage(String pdfFilePath, int dpi) throws IOException {
        PDDocument document = PDDocument.load(new File(pdfFilePath));
        PDFRenderer renderer = new PDFRenderer(document);

        // Render the first page to an image with DPI setting
        BufferedImage image = renderer.renderImageWithDPI(0, dpi);

        // Convert the color image to grayscale
        BufferedImage grayscaleImage = new BufferedImage(image.getWidth(), image.getHeight(), BufferedImage.TYPE_BYTE_GRAY);
        Graphics2D graphics = grayscaleImage.createGraphics();
        graphics.drawImage(image, 0, 0, null);
        graphics.dispose();

        return grayscaleImage;
    }

    private static BufferedImage grayscaleToBlackAndWhite(BufferedImage grayscaleImage) {
        BufferedImage blackAndWhiteImage = new BufferedImage(grayscaleImage.getWidth(), grayscaleImage.getHeight(), BufferedImage.TYPE_BYTE_BINARY);
        int threshold = 128; // Adjust this value (0-255) to control black and white threshold (higher for darker)

        for (int y = 0; y < grayscaleImage.getHeight(); y++) {
            for (int x = 0; x < grayscaleImage.getWidth(); x++) {
                int grayscaleValue = grayscaleImage.getRaster().getSample(x, y, 0);
                blackAndWhiteImage.getRaster().setPixel(x, y, grayscaleValue > threshold ? 255 : 0);
            }
        }

        return blackAndWhiteImage;
    }

    private static void writeImageToFile(RenderedImage image, String filePath, String format) throws IOException {
        ImageIO.write(image, format, new File(filePath));
    }
}
