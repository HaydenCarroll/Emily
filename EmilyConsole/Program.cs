using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Speech.Recognition;
using System.Text;
using System.Threading.Tasks;

namespace EmilyConsole
{
    class Program
    {
        //look into word2vec and dialog flow
        private static SystemFiles sf;
        private static SpeechRecognitionEngine speechRecognizer = new SpeechRecognitionEngine();
        static void Main(string[] args)
        {
            /*speechRecognizer.SpeechRecognized += process;

            GrammarBuilder grammarBuilder = new GrammarBuilder();
            Choices commandChoices = new Choices("weight", "color", "size");
            grammarBuilder.Append(commandChoices);

            Choices valueChoices = new Choices();
            valueChoices.Add("normal", "bold");
            valueChoices.Add("red", "green", "blue");
            valueChoices.Add("small", "medium", "large");
            grammarBuilder.Append(valueChoices);

            speechRecognizer.LoadGrammar(new Grammar(grammarBuilder));
            speechRecognizer.SetInputToDefaultAudioDevice();*/

            //request drive letter
            Console.WriteLine("Input Main Drive Letter");
            string input = Console.ReadLine();
            while(input.Length > 1 || input.Length < 1)
            {
                Console.WriteLine("Invalid drive letter! Please use single letter (ex. \'C\')");
                Console.WriteLine("Input Main Drive Letter");
                input = Console.ReadLine();
            }
            sf = new SystemFiles(input);
            Console.Clear();
            while (true)
            {
                Run();
            }
        }

       

        static void Run()
        {
            //Console.WriteLine(GetActiveWindowTitle());
            //System.Threading.Thread.Sleep(100);
            Console.WriteLine("Input");
            string input = Console.ReadLine();
            process(input);
        }

        


        static void process(string input)
        {
            
            //Console.WriteLine(input);
            //for file searching
            if (input.Contains("find") || input.Contains("show"))
            {
                string[] seporator = { " find ", " show ", "find", "show", "find ", "show " };
                string[] split = input.Split(seporator,StringSplitOptions.RemoveEmptyEntries);
                if (split.Length > 1)
                {
                    string search = split[split.Length - 1];
                    if(search[0] == ' ')
                    {
                        search = search.Substring(1);
                    }
                    
                    sf.find_file(search);
                }
                else
                {
                    string search = split[0];
                    if (search[0] == ' ')
                    {
                        search = search.Substring(1);
                    }
                    sf.find_file(search);
                }
            }

            //for opening file
            if (input.Contains("open") || input.Contains("start") || input.Contains("run"))
            {
                string[] seporator = { " open ", " start ", " run ", "open", "start","run", "open ", "start ", "run " };
                string[] split = input.Split(seporator, StringSplitOptions.RemoveEmptyEntries);
                if (split.Length > 1)
                {
                    string search = split[split.Length - 1];
                    if (search[0] == ' ')
                    {
                        search = search.Substring(1);
                    }
                    sf.open_file(search);
                }
                else
                {
                    string search = split[0];
                    if (search[0] == ' ')
                    {
                        search = search.Substring(1);
                    }
                    sf.open_file(search);
                }
            }

        }

        [DllImport("user32.dll")]
        static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

        
        private static string GetActiveWindowTitle()
        {
            const int nChars = 256;
            StringBuilder Buff = new StringBuilder(nChars);
            IntPtr handle = GetForegroundWindow();

            if (GetWindowText(handle, Buff, nChars) > 0)
            {
                string current_window = Buff.ToString();
                ConcurrentStack<char> reverseStack = new ConcurrentStack<char>();
                foreach (char c in current_window) reverseStack.Push(c);
                string window = "";
                foreach(char c in reverseStack)
                {
                    char cur;
                    reverseStack.TryPop(out cur);
                    if(cur == '\\' || cur == '/')
                    {
                        break;
                    }
                    if (cur == ' ')
                    {
                        char peek;
                        reverseStack.TryPeek(out peek);
                        if(peek == '-') break;
                    }
                    window += cur;
                }
                char[] post_reverse = window.ToCharArray();
                Array.Reverse(post_reverse);
                window = "";
                foreach (char c in post_reverse) window += c;
                return window;
            }
            return "Desktop";
        }
    }
}
