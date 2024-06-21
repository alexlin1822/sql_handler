using System;
using System.Drawing;
using System.Drawing.Imaging;
using ZXing;
using ZXing.Common;
using ZXing.QrCode;

namespace PDFtoImage
{
    internal class zx
    {
        static void Main(string[] args)
        {
            string pdfPath = "D:\\MyProgram\\CSharp\\PDFtoImage\\Page_1.png";
            string outputPath = "D:\\MyProgram\\CSharp\\PDFtoImage\\output11.png";

            ExtractAndSaveQRCode(pdfPath, outputPath);
        }


        static void ExtractAndSaveQRCode(string inputImagePath, string outputImagePath)
        {
            using (Bitmap bitmap = new Bitmap(inputImagePath))
            {
                LuminanceSource source = new BitmapLuminanceSource(bitmap);
                /*BinaryBitmap binaryBitmap = new BinaryBitmap(new HybridBinarizer(source));*/

                IBarcodeReader reader = new BarcodeReader();
                var result = reader.Decode(source);

                if (result != null)
                {
                    var points = result.ResultPoints;
                    if (points.Length >= 4)
                    {
                        int minX = (int)Math.Min(Math.Min(points[0].X, points[1].X), Math.Min(points[2].X, points[3].X));
                        int maxX = (int)Math.Max(Math.Max(points[0].X, points[1].X), Math.Max(points[2].X, points[3].X));
                        int minY = (int)Math.Min(Math.Min(points[0].Y, points[1].Y), Math.Min(points[2].Y, points[3].Y));
                        int maxY = (int)Math.Max(Math.Max(points[0].Y, points[1].Y), Math.Max(points[2].Y, points[3].Y));

                        int width = maxX - minX;
                        int height = maxY - minY;

                        // Create a new white background image
                        using (Bitmap newImage = new Bitmap(bitmap.Width, bitmap.Height))
                        {
                            using (Graphics g = Graphics.FromImage(newImage))
                            {
                                // Fill the new image with white background
                                g.Clear(Color.White);

                                // Draw the QR code onto the new image
                                Rectangle sourceRect = new Rectangle(minX, minY, width, height);
                                Rectangle destRect = new Rectangle(minX, minY, width, height);
                                g.DrawImage(bitmap, destRect, sourceRect, GraphicsUnit.Pixel);
                            }

                            // Save the new image
                            newImage.Save(outputImagePath, ImageFormat.Png);
                            Console.WriteLine($"QR code saved as {outputImagePath}");
                        }
                    }
                    else
                    {
                        Console.WriteLine("QR code detection points are insufficient.");
                    }
                }
                else
                {
                    Console.WriteLine("No QR code detected in the image.");
                }
            }
        }
    }

    public class BitmapLuminanceSource : BaseLuminanceSource
    {
        public BitmapLuminanceSource(Bitmap bitmap) : base(bitmap.Width, bitmap.Height)
        {
            var data = new byte[bitmap.Width * bitmap.Height * 4];
            var rect = new Rectangle(0, 0, bitmap.Width, bitmap.Height);
            var bitmapData = bitmap.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            System.Runtime.InteropServices.Marshal.Copy(bitmapData.Scan0, data, 0, data.Length);
            bitmap.UnlockBits(bitmapData);

            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    var offset = (y * Width + x) * 4;
                    var r = data[offset];
                    var g = data[offset + 1];
                    var b = data[offset + 2];
                    var gray = (r + g + b) / 3;
                    luminances[y * Width + x] = (byte)gray;
                }
            }
        }

        protected override LuminanceSource CreateLuminanceSource(byte[] newLuminances, int width, int height)
        {
            return new BitmapLuminanceSource(newLuminances, width, height);
        }

        public BitmapLuminanceSource(byte[] luminances, int width, int height) : base(luminances, width, height)
        {
        }

    }
}







