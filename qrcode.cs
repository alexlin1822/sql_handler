using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using iTextSharp.text.pdf;
using PdfiumViewer;
using ZXing;

class Program
{
    static void Main(string[] args)
    {
        string pdfPath = "path/to/your/pdf_with_qr_code.pdf";
        string outputImagePath = "path/to/output/qr_code_image.png";

        // Extract the QR code image from the PDF
        Bitmap qrCodeImage = ExtractQRCodeImageFromPdf(pdfPath);

        // Save the QR code image as PNG
        qrCodeImage.Save(outputImagePath, ImageFormat.Png);

        Console.WriteLine("QR code image saved to " + outputImagePath);
    }

    static Bitmap ExtractQRCodeImageFromPdf(string pdfPath)
    {
        // Load the PDF document
        using (var document = PdfDocument.Load(pdfPath))
        {
            // Convert the first page to an image (assuming the QR code is on the first page)
            var page = document.Render(0, 300, 300, PdfRenderFlags.CorrectFromDpi);

            // Decode the QR code from the rendered page image
            IBarcodeReader reader = new BarcodeReader();
            var result = reader.Decode(page);

            if (result != null)
            {
                // Get the QR code rectangle
                var points = result.ResultPoints;
                if (points.Length >= 4)
                {
                    int minX = (int)Math.Min(Math.Min(points[0].X, points[1].X), Math.Min(points[2].X, points[3].X));
                    int maxX = (int)Math.Max(Math.Max(points[0].X, points[1].X), Math.Max(points[2].X, points[3].X));
                    int minY = (int)Math.Min(Math.Min(points[0].Y, points[1].Y), Math.Min(points[2].Y, points[3].Y));
                    int maxY = (int)Math.Max(Math.Max(points[0].Y, points[1].Y), Math.Max(points[2].Y, points[3].Y));

                    int width = maxX - minX;
                    int height = maxY - minY;

                    // Crop the QR code from the page image
                    var qrCodeImage = new Bitmap(width, height);
                    using (Graphics g = Graphics.FromImage(qrCodeImage))
                    {
                        g.DrawImage(page, new Rectangle(0, 0, width, height), new Rectangle(minX, minY, width, height), GraphicsUnit.Pixel);
                    }

                    return qrCodeImage;
                }
            }

            throw new Exception("QR code not found in the PDF.");
        }
    }
}
