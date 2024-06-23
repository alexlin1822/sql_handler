import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class GrayscaleToBWConverter {

    public static void main(String[] args) {
        String grayscaleImagePath = "path/to/output/image.png";
        String bwOutputPath = "path/to/output/image_bw.png";
        int threshold = 128;  // Adjust the threshold between 0 to 255

        try {
            BufferedImage grayscaleImage = ImageIO.read(new File(grayscaleImagePath));
            BufferedImage bwImage = new BufferedImage(grayscaleImage.getWidth(), grayscaleImage.getHeight(), BufferedImage.TYPE_BYTE_BINARY);

            for (int x = 0; x < grayscaleImage.getWidth(); x++) {
                for (int y = 0; y < grayscaleImage.getHeight(); y++) {
                    int gray = (grayscaleImage.getRGB(x, y) & 0xFF);
                    int bw = gray < threshold ? 0x00 : 0xFF;
                    bwImage.setRGB(x, y, (bw << 16) | (bw << 8) | bw);
                }
            }

            ImageIO.write(bwImage, "png", new File(bwOutputPath));

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
