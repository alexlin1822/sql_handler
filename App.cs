
using System;
using System.IO;
using System.Diagnostics;

namespace PdfToBlackWhitePng
{
    class App
    {
        /**
         *  Convert PDF file to PNG file
        */
        public static void Main(string[] args)
        {
            // Hint for User
            Console.WriteLine("PDF to PNG for Label \n");
            Console.WriteLine("Usage: \"<Param1: Input PDF file path and name>\" \"<Param2: Output Landscape PNG file folder path>\" \"<Param3: Output Portrait PNG file folder path>\" \"<Param4: Temporary file folder path>\" \"<Param5: Output DPI [Must > 1]>\" \"<param6: Threshold of QR code [Between 1 to 254]>\"");
            Console.WriteLine("Windows Example:  pdf2png.exe \"c:\\pdf_folder\\english_label1.pdf;c:\\pdf_folder\\english_label2.pdf\" \"c:\\pdf_folder\\output\\Landscape\" \"c:\\pdf_folder\\output\\Portrait\" \"c:\\pdf_folder\\output\\Tmp\" \"152\" \"190\"");
            Console.WriteLine("Linux Example:  dotnet run \"/pdf_folder/english_label1.pdf;/pdf_folder/english_label2.pdf\" \"/pdf_folder/output/Landscape\" \"/pdf_folder/output/Portrait\" \"/pdf_folder/output/Tmp\" \"152\" \"190\"");
            Console.WriteLine("                       ");
            Console.WriteLine("\n");

            //Initial params
            string currentDir = Directory.GetCurrentDirectory();

            string outputPathLandscape = currentDir + "\\output\\Landscape";
            string outputPathPortrait = currentDir + "\\output\\Portrait";
            string tempImagePath = currentDir + "\\tmp";

            string dpi = "152";
            string threshold = "190";

            // List<string> labels = new List<string> { "AC765241", "Arabic", "Bulgarian", "english", "French", "German", "Hebrew", "Japanese", "Korean", "Polish", "Thai" };
            // List<string> labels = new List<string> { "French"};
            // List<string> labels = new List<string> { "english"};
            // List<string> labels = new List<string> { "DDL-29inch-125dpi-Page1","DDL-29inch-125dpi-Page2" };
            List<string> labels = new List<string> { "Arabic", "Bulgarian", "english", "French", "German", "Hebrew", "Japanese", "Korean", "Polish", "Thai", "DDL-29inch-125dpi" };
            for (int i = 0; i < labels.Count; i++)
            {
                labels[i] = currentDir + "\\input\\" + labels[i] + ".pdf";
            }


            //If User has custom params. Get it.
            //Local testing command line:
            if (args.Length == 6)
            {
                labels.Clear();
                string[] files = args[0].Split(";");
                for (int j = 0; j < files.Length; j++)
                {
                    labels.Add(files[0]);
                }

                outputPathLandscape = args[1];
                outputPathPortrait = args[2];
                tempImagePath = args[3];

                if (IsNumberInRange(dpi, 1, 10000000))
                {
                    dpi = args[4];
                }
                if (IsNumberInRange(dpi, 1, 254))
                {
                    threshold = args[5];
                }
            }

            if (!Directory.Exists(outputPathLandscape))
            {
                Directory.CreateDirectory(outputPathLandscape);
                Console.WriteLine("Created Directory: " + outputPathLandscape);
            }

            if (!Directory.Exists(outputPathPortrait))
            {
                Directory.CreateDirectory(outputPathPortrait);
                Console.WriteLine("Created Directory: " + outputPathPortrait);
            }

            if (!Directory.Exists(tempImagePath))
            {
                Directory.CreateDirectory(tempImagePath);
                Console.WriteLine("Created Directory: " + tempImagePath);
            }

            // Call function to convert PDF to PNG
            foreach (string pdfFilePathAndName in labels)
            {

                Console.WriteLine("-------------PDF to PNG, converting......----------------------");
                Stopwatch stopwatch = new Stopwatch();
                stopwatch.Start();

                if (File.Exists(pdfFilePathAndName))
                {
                    //Invoking JAVA Library to generate QR code image, then pasted the text to png image. 
                    ConversionWithJavaLib.ConvertPdfToBlackWhitePng(pdfFilePathAndName, outputPathLandscape, outputPathPortrait, tempImagePath, dpi, threshold);
                }
                else
                {
                    Console.WriteLine("PDF file not found! " + pdfFilePathAndName);
                }
                stopwatch.Stop();
                Console.WriteLine("Total spent time: " + stopwatch.ElapsedMilliseconds + " ms");
                Console.WriteLine("-----------------------------------------");
                Console.WriteLine("      ");
            }
        }

        /**
         * Check if a string is a number and in the range 
         * @param str  		String of number
         * @param min       Minimum of number
         * @param max       Maximum of number
         * @return          Boolean
         */
        private static bool IsNumberInRange(string str, int min, int max)
        {
            if (int.TryParse(str, out int number))
            {
                if (number >= min && number <= max)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
