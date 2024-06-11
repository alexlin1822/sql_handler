import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;
import org.apache.pdfbox.rendering.ImageType;

import javax.imageio.ImageIO;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class PDFToBWImage {

    public static void main(String[] args) {
        // Path to the input PDF and output PNG image
        String inputPDFPath = "path/to/input.pdf";
        String outputImagePath = "path/to/output.png";

        try {
            // Load the PDF document
            PDDocument document = PDDocument.load(new File(inputPDFPath));

            // Create a PDF renderer
            PDFRenderer pdfRenderer = new PDFRenderer(document);

            // Render the first page to an image
            BufferedImage colorImage = pdfRenderer.renderImageWithDPI(0, 300, ImageType.RGB);

            // Convert to black and white
            BufferedImage bwImage = new BufferedImage(
                    colorImage.getWidth(), colorImage.getHeight(),
                    BufferedImage.TYPE_BYTE_BINARY);

            Graphics2D graphics = bwImage.createGraphics();
            graphics.drawImage(colorImage, 0, 0, null);
            graphics.dispose();

            // Save the black and white image
            ImageIO.write(bwImage, "png", new File(outputImagePath));

            // Close the document
            document.close();

            System.out.println("PDF page converted to black and white PNG successfully.");

        } catch (IOException ex) {
            System.out.println("Error during PDF processing: " + ex.getMessage());
            ex.printStackTrace();
        }
    }
}
