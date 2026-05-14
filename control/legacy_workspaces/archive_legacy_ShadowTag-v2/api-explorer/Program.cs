using System;
using System.Linq;
using System.Reflection;
using Microsoft.SemanticKernel;

// Trying to find where ProcessBuilder is and what it has
namespace ApiExplorer;

class Program
{
    static void Main(string[] args)
    {
        try
        {
            // Load the assembly containing ProcessBuilder
            var asm = typeof(Microsoft.SemanticKernel.ProcessBuilder).Assembly;
            Console.WriteLine($"Assembly: {asm.FullName}");

            Console.WriteLine("\n--- Types in Microsoft.SemanticKernel.Process* namespace ---");
            foreach (var t in asm.GetTypes().Where(t => t.FullName != null && t.FullName.StartsWith("Microsoft.SemanticKernel")))
            {
                Console.WriteLine($"Type: {t.Name} ({t.FullName})");

                if (t.Name == "ProcessFunctionTargetBuilder")
                {
                     Console.WriteLine("  Constructors:");
                     foreach (var c in t.GetConstructors())
                     {
                         Console.WriteLine($"    - {t.Name}({string.Join(", ", c.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
                     }
                }

                // List public methods for ProcessBuilder and related classes
                if (t.Name.Contains("Process") || t.Name.Contains("Step"))
                {
                    Console.WriteLine("  Methods:");
                    foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
                    {
                        Console.WriteLine($"    - {m.ReturnType.Name} {m.Name}({string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
                    }
                    Console.WriteLine("  Static Methods:");
                    foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly))
                    {
                        Console.WriteLine($"    - {m.ReturnType.Name} {m.Name}({string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
        }
    }
}
