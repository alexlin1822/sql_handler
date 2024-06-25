package com.pdf2png;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.io.RandomAccessReadBufferedFile;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;
import org.apache.pdfbox.rendering.ImageType;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;


/**
 * PDF file to PNG file conversion
 * 
 * @param 1 Input PDF file path and name
 * @param 2 Output PNG file path and name
 * @param 3 PDF Page_number
 * @param 4 Output DPI
 * @param 5 threshold	Control document darker or lighter. Adjust the threshold between 0 to 255. 0 is lighter. 255 is darker.
 */
public class App {
	public static void main(String[] args) {
		if (args.length != 5) {
			System.err.println(
					"Usage: <Param1: Input PDF file path and name> <Param2: Output PNG file path and name> <Param3: PDF Page number> <Param4: Output DPI> <param5: Threshold>");
			System.err.println("args number: " + args.length);
			for (int i = 0; i < args.length; i++) {
				System.err.println("args " + i + "=" + args[i]);
			}
			System.exit(1);
		}

		String inputPDFPath = args[0];
		String outputImagePath_bw = args[1];
		int pageNumber = 0;
		int dpi=152;
		int threshold = 190; 

		try {
			pageNumber=Integer.parseInt(args[2]);
		}catch(Exception e) {
			pageNumber=0;
		}
		
		try {
			dpi=Integer.parseInt(args[3]);
		}catch(Exception e) {
			dpi=152;
		}

		try {
			threshold=Integer.parseInt(args[4]);
		}catch(Exception e) {
			threshold=190;
		}
		
		long startTime= System.currentTimeMillis();
		
		//Convert PDF to PNG image with custom parameter
		pdf_custom(inputPDFPath, outputImagePath_bw, pageNumber,dpi,threshold);
		
		long endTime= System.currentTimeMillis();
		
		System.out.println("Java PDF to PNG running time: "+(endTime-startTime)+" ms");
	}

	/**
	 * Convert PDF to PNG image with custom parameter
	 * @param inputPDFPath  		Input PDF file path and name
	 * @param outputImagePath_bw	Output PNG file path and name
	 * @param pageNumber			PDF Page_number
	 * @param dpi					Output DPI
	 * @param threshold				Control document darker or lighter. Adjust the threshold between 0 to 255. 0 is lighter. 255 is darker.
	 */
	public static void pdf_custom(String inputPDFPath, String outputImagePath_bw, int pageNumber, int dpi,int threshold) {

		try (PDDocument document = Loader.loadPDF(new RandomAccessReadBufferedFile(inputPDFPath))) {
			// Create a PDF renderer
			PDFRenderer pdfRenderer = new PDFRenderer(document);

			//Convert page to Grayscale image, then save.
			BufferedImage grayscaleImage = pdfRenderer.renderImageWithDPI(pageNumber, dpi, ImageType.GRAY);

			BufferedImage bwImage = new BufferedImage(grayscaleImage.getWidth(), grayscaleImage.getHeight(),
					BufferedImage.TYPE_BYTE_GRAY);

			for (int x = 0; x < grayscaleImage.getWidth(); x++) {
				for (int y = 0; y < grayscaleImage.getHeight(); y++) {
					int gray = (grayscaleImage.getRGB(x, y) & 0xFF);
					int bw = gray < threshold ? 0x00 : 0xFF;
					bwImage.setRGB(x, y, (bw << 16) | (bw << 8) | bw);
				}
			}

			ImageIO.write(bwImage, "png", new File(outputImagePath_bw));

			System.out.println("QR code conversion completed!");
		} catch (IOException e) {
			e.printStackTrace();
			System.err.println("PDF Conversion Error");
		}
	}

}
