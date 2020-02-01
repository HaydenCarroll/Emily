﻿using System;

public class SystemFiles
{
    private static List<string> all_files;
    public SystemFiles()
	{
        all_files = new List<string>();
        initalize_files();
	}

    private static void initalize_files()
    {
        string userName = trimToBackslash(System.Security.Principal.WindowsIdentity.GetCurrent().Name);
        all_files = getAllFiles(@"C:\Users\" + userName + "\\", new List<string>());
        all_files.AddRange(getAllFiles(@"C:\Program Files\", new List<string>()));
        all_files.AddRange(getAllFiles(@"C:\Program Files (x86)\", new List<string>()));
        all_files.AddRange(getAllFiles(@"C:\Users\" + userName + "\\Downloads\\", new List<string>()));
        all_files.AddRange(getAllFiles(@"C:\Users\" + userName + "\\Pictures\\", new List<string>()));
    }

    //for opening/executing file
    public static void open_file(string input)
    {
        string search_item = input;
        List<string[]> rankedFiles = new List<string[]>();
        bool hasRefinedList = false;
        List<string[]> refinedList = new List<string[]>();
        //for exact matches
        foreach (string s in all_files)
        {

            if (s.ToLower().Contains(input.ToLower()))
            {
                string[] sa = { s, Jaro_Winkler_score(input, trimToBackslash(s)) + "" };
                refinedList.Add(sa);
                hasRefinedList = true;
                //Console.WriteLine("Match: " + s);
            }
        }
        if (hasRefinedList)
        {
            rankedFiles = refinedList;
        }
        // if no exact match is found
        else
        {
            foreach (string s in all_files)
            {
                //Levenshtein distance
                //string[] sa = { s, levenshtein_distance(input, trimToBackslash(s))+"" };
                //Jaro-Winkler
                string[] sa = { s, Jaro_Winkler_score(input, s) + "" };
                rankedFiles.Add(sa);
            }
        }

        //Levenshtein distance
        //rankedFiles = rankedFiles.OrderBy(arr => Int32.Parse(arr[1])).ToList();
        //Jaro-Winkler
        rankedFiles = rankedFiles.OrderBy(arr => double.Parse(arr[1])).ToList();
        //rankedFiles.Reverse();
        int count = 0;
        string topFile = rankedFiles[0][0];
        System.Diagnostics.Process.Start(@topFile);
        foreach (string[] k in rankedFiles)
        {
            if (count >= 5)
            {
                break;
            }
            Console.WriteLine(k[0] + " score:" + k[1]);
            count++;
        }
        Console.WriteLine(input);
    }

    //for finding and opening file location
    public static void find_file(string input)
    {
        string search_item = input;
        List<string[]> rankedFiles = new List<string[]>();
        bool hasRefinedList = false;
        List<string[]> refinedList = new List<string[]>();
        foreach (string s in all_files)
        {

            if (s.ToLower().Contains(input.ToLower()))
            {
                string[] sa = { s, Jaro_Winkler_score(input, trimToBackslash(s)) + "" };
                refinedList.Add(sa);
                hasRefinedList = true;
                //Console.WriteLine("Match: " + s);
            }
        }
        if (hasRefinedList)
        {
            rankedFiles = refinedList;
        }
        else
        {
            foreach (string s in all_files)
            {
                //Levenshtein distance
                //string[] sa = { s, levenshtein_distance(input, trimToBackslash(s))+"" };
                //Jaro-Winkler
                string[] sa = { s, Jaro_Winkler_score(input, s) + "" };
                rankedFiles.Add(sa);
            }
        }

        //Levenshtein distance
        //rankedFiles = rankedFiles.OrderBy(arr => Int32.Parse(arr[1])).ToList();
        //Jaro-Winkler
        rankedFiles = rankedFiles.OrderBy(arr => double.Parse(arr[1])).ToList();
        //rankedFiles.Reverse();
        int count = 0;
        string topFile = rankedFiles[0][0];
        System.Diagnostics.Process.Start(@getParentFolder(topFile));
        foreach (string[] k in rankedFiles)
        {
            if (count >= 5)
            {
                break;
            }
            Console.WriteLine(k[0] + " score:" + k[1]);
            count++;
        }
        Console.WriteLine(input);
    }

    private static List<string> getAllFiles(string dir, List<string> l)
    {
        string[] dirs;
        try
        {
            dirs = Directory.GetDirectories(dir);
            //Console.WriteLine("Searching " + dir);

        }
        catch (System.Exception excpt)
        {
            Console.WriteLine("Exception " + excpt.Message);
            return l;
        }
        foreach (string d in dirs)
        {
            string[] files;
            try
            {
                files = Directory.GetFiles(d);
            }
            catch (System.Exception excpt)
            {
                //Console.WriteLine("Exception " + excpt.Message);
                continue;
            }
            foreach (string f in files)
            {
                //Console.WriteLine(f);
                l.Add(f);
                //l.Add(trimToBackslash(f));
            }
            getAllFiles(d, l);
        }
        return l;
    }
    

    private static string getParentFolder(string s)
    {
        char[] reverseCharArray = s.ToCharArray();
        Array.Reverse(reverseCharArray);
        int index = 0;
        foreach (char c in reverseCharArray)
        {
            if (c == '\\')
            {
                break;
            }
            index++;
        }
        string parentString = "";
        Array.Reverse(reverseCharArray);
        for (int i = 0; i < reverseCharArray.Length - (index + 1); i++)
        {
            parentString += reverseCharArray[i];
        }
        return parentString;
    }

    private static string trimToBackslash(string s)
    {
        ConcurrentStack<char> reverseStack = new ConcurrentStack<char>();
        foreach (char c in s) reverseStack.Push(c);
        string newString = "";
        foreach (char c in reverseStack)
        {
            char cur;
            reverseStack.TryPop(out cur);
            if (cur == '\\')
            {
                break;
            }
            newString += cur;
        }
        char[] post_reverse = newString.ToCharArray();
        Array.Reverse(post_reverse);
        newString = "";
        foreach (char c in post_reverse) newString += c;
        return newString;
    }

    private static double lcs(String X, String Y)
    {
        int m = X.Length;
        int n = Y.Length;

        int[,] LCSuff = new int[m + 1, n + 1];


        int len = 0;

        int row = 0, col = 0;

        for (int i = 0; i <= m; i++)
        {
            for (int j = 0; j <= n; j++)
            {
                if (i == 0 || j == 0)
                    LCSuff[i, j] = 0;

                else if (X[i - 1] == Y[j - 1])
                {
                    LCSuff[i, j] = LCSuff[i - 1, j - 1] + 1;
                    if (len < LCSuff[i, j])
                    {
                        len = LCSuff[i, j];
                        row = i;
                        col = j;
                    }
                }
                else
                    LCSuff[i, j] = 0;
            }
        }

        // if true, then no common substring exists 
        if (len == 0)
        {
            return 1;
        }


        String resultStr = "";

        while (LCSuff[row, col] != 0)
        {
            resultStr = X[row - 1] + resultStr; // or Y[col-1] 
            --len;

            // move diagonally up to previous cell 
            row--;
            col--;
        }

        return 1 / resultStr.Length;
    }

    private static int levenshtein_distance(string s, string t)
    {
        if (string.IsNullOrEmpty(s))
        {
            if (string.IsNullOrEmpty(t))
                return 0;
            return t.Length;
        }

        if (string.IsNullOrEmpty(t))
        {
            return s.Length;
        }

        int n = s.Length;
        int m = t.Length;
        int[,] d = new int[n + 1, m + 1];

        // initialize the top and right of the table to 0, 1, 2, ...
        for (int i = 0; i <= n; d[i, 0] = i++) ;
        for (int j = 1; j <= m; d[0, j] = j++) ;

        for (int i = 1; i <= n; i++)
        {
            for (int j = 1; j <= m; j++)
            {
                int cost = (t[j - 1] == s[i - 1]) ? 0 : 1;
                int min1 = d[i - 1, j] + 1;
                int min2 = d[i, j - 1] + 1;
                int min3 = d[i - 1, j - 1] + cost;
                d[i, j] = Math.Min(Math.Min(min1, min2), min3);
            }
        }
        return d[n, m];
    }

    private static double Jaro_Winkler_score(string aString1, string aString2)
    {
        return 1.0 - proximity(aString1, aString2);
    }

    private static readonly double mWeightThreshold = 0.7;
    private static readonly int mNumChars = 2;
    private static double proximity(string aString1, string aString2)
    {
        int lLen1 = aString1.Length;
        int lLen2 = aString2.Length;
        if (lLen1 == 0)
            return lLen2 == 0 ? 1.0 : 0.0;

        int lSearchRange = Math.Max(0, Math.Max(lLen1, lLen2) / 2 - 1);

        // default initialized to false
        bool[] lMatched1 = new bool[lLen1];
        bool[] lMatched2 = new bool[lLen2];

        int lNumCommon = 0;
        for (int i = 0; i < lLen1; ++i)
        {
            int lStart = Math.Max(0, i - lSearchRange);
            int lEnd = Math.Min(i + lSearchRange + 1, lLen2);
            for (int j = lStart; j < lEnd; ++j)
            {
                if (lMatched2[j]) continue;
                if (aString1[i] != aString2[j])
                    continue;
                lMatched1[i] = true;
                lMatched2[j] = true;
                ++lNumCommon;
                break;
            }
        }
        if (lNumCommon == 0) return 0.0;

        int lNumHalfTransposed = 0;
        int k = 0;
        for (int i = 0; i < lLen1; ++i)
        {
            if (!lMatched1[i]) continue;
            while (!lMatched2[k]) ++k;
            if (aString1[i] != aString2[k])
                ++lNumHalfTransposed;
            ++k;
        }
        // System.Diagnostics.Debug.WriteLine("numHalfTransposed=" + numHalfTransposed);
        int lNumTransposed = lNumHalfTransposed / 2;

        // System.Diagnostics.Debug.WriteLine("numCommon=" + numCommon + " numTransposed=" + numTransposed);
        double lNumCommonD = lNumCommon;
        double lWeight = (lNumCommonD / lLen1
                         + lNumCommonD / lLen2
                         + (lNumCommon - lNumTransposed) / lNumCommonD) / 3.0;

        if (lWeight <= mWeightThreshold) return lWeight;
        int lMax = Math.Min(mNumChars, Math.Min(aString1.Length, aString2.Length));
        int lPos = 0;
        while (lPos < lMax && aString1[lPos] == aString2[lPos])
            ++lPos;
        if (lPos == 0) return lWeight;
        return lWeight + 0.1 * lPos * (1.0 - lWeight);

    }
}
