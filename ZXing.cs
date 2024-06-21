using System;
using System.Drawing;
using System.Drawing.Imaging;
using PdfiumViewer;
using ZXing;

class Program
{
    static void Main(string[] args)
    {
        string pdfPath = "path/to/your/pdf_with_qr_code.pdf";
        string outputImagePath = "path/to/output/image.png";

        // Convert the PDF to an 8-bit black and white PNG image
        ConvertPdfToBlackAndWhiteImage(pdfPath, outputImagePath);

        Console.WriteLine("Image saved to " + outputImagePath);
    }

    static void ConvertPdfToBlackAndWhiteImage(string pdfPath, string outputImagePath)
    {
        // Load the PDF document
        using (var document = PdfDocument.Load(pdfPath))
        {
            // Render the first page to an image (assuming the QR code and text are on the first page)
            var page = document.Render(0, 300, 300, PdfRenderFlags.CorrectFromDpi);

            // Convert the rendered page to an 8-bit black and white image
            var bwImage = ConvertToBlackAndWhite(page);

            // Save the black and white image as PNG
            bwImage.Save(outputImagePath, ImageFormat.Png);
        }
    }

    static Bitmap ConvertToBlackAndWhite(Bitmap original)
    {
        // Create a new bitmap with the same dimensions
        var bwImage = new Bitmap(original.Width, original.Height, PixelFormat.Format8bppIndexed);

        // Set the palette to grayscale
        var palette = bwImage.Palette;
        for (int i = 0; i < 256; i++)
        {
            palette.Entries[i] = Color.FromArgb(i, i, i);
        }
        bwImage.Palette = palette;

        // Lock the bits of the original and new bitmap
        var originalData = original.LockBits(new Rectangle(0, 0, original.Width, original.Height), ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
        var bwData = bwImage.LockBits(new Rectangle(0, 0, bwImage.Width, bwImage.Height), ImageLockMode.WriteOnly, PixelFormat.Format8bppIndexed);

        // Copy pixel data, converting to grayscale
        unsafe
        {
            for (int y = 0; y < original.Height; y++)
            {
                byte* originalRow = (byte*)originalData.Scan0 + (y * originalData.Stride);
                byte* bwRow = (byte*)bwData.Scan0 + (y * bwData.Stride);

                for (int x = 0; x < original.Width; x++)
                {
                    byte b = originalRow[x * 3];
                    byte g = originalRow[x * 3 + 1];
                    byte r = originalRow[x * 3 + 2];

                    // Calculate luminance using the Rec. 709 formula
                    byte gray = (byte)(0.2126 * r + 0.7152 * g + 0.0722 * b);

                    bwRow[x] = gray;
                }
            }
        }

        // Unlock the bits
        original.UnlockBits(originalData);
        bwImage.UnlockBits(bwData);

        return bwImage;
    }
}
