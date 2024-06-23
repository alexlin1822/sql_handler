using System;
using System.Diagnostics;

namespace RunJavaJar
{
    class Program
    {
        static void Main(string[] args)
        {
            // Path to the Java executable
            string javaPath = "java";
            
            // Path to the JAR file
            string jarPath = "C:/path/to/your/CommandLineArgsExample.jar";

            // Parameters to pass to the Java application
            string param1 = "hello";
            string param2 = "world";

            // Create the process start info
            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = javaPath;
            startInfo.Arguments = $"-jar \"{jarPath}\" {param1} {param2}";
            startInfo.UseShellExecute = false;
            startInfo.RedirectStandardOutput = true;
            startInfo.RedirectStandardError = true;

            try
            {
                // Start the process
                using (Process process = new Process())
                {
                    process.StartInfo = startInfo;
                    process.Start();

                    // Read the output (or error)
                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();

                    process.WaitForExit();

                    // Display the output
                    Console.WriteLine("Output:");
                    Console.WriteLine(output);

                    // Display the error (if any)
                    if (!string.IsNullOrEmpty(error))
                    {
                        Console.WriteLine("Error:");
                        Console.WriteLine(error);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred while trying to run the Java application.");
                Console.WriteLine(ex.Message);
            }
        }
    }
}
