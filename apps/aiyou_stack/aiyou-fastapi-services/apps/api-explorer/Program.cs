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
            var asm = typeof(Microsoft.SemanticKernel.ProcessBuilder).Assembly;
            Console.WriteLine($"Assembly: {asm.FullName}");

            var type = typeof(Microsoft.SemanticKernel.ProcessBuilder);
            Console.WriteLine($"Type: {type.FullName}");
            
            Console.WriteLine("Methods:");
            foreach (var m in type.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
            {
                Console.WriteLine($" - {m.ReturnType.Name} {m.Name}({string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
                
                // Inspect return type if it's interesting
                if (m.Name.StartsWith("On") || m.Name.StartsWith("Add")) {
                     Console.WriteLine($"   -> Methods on {m.ReturnType.Name}:");
                     foreach(var rm in m.ReturnType.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
                        Console.WriteLine($"      - {rm.ReturnType.Name} {rm.Name}({string.Join(", ", rm.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
                }
            }
            
            Console.WriteLine("\nExtensions on ProcessBuilder?");
            // This is harder to find without scanning all assemblies, but let's check the type itself first.
            
            Console.WriteLine("\nType: Microsoft.SemanticKernel.ProcessFunctionTargetBuilder");
            var targetType = typeof(Microsoft.SemanticKernel.ProcessFunctionTargetBuilder);
            Console.WriteLine("Methods:");
            // Check constructors too
            foreach (var c in targetType.GetConstructors())
            {
                Console.WriteLine($" - Constructor({string.Join(", ", c.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
            }
            foreach (var m in targetType.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
            {
                Console.WriteLine($" - {m.ReturnType.Name} {m.Name}({string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name))})");
            }

            // Check for ProcessFunctionTarget by string name to avoid compile error if it doesn't exist
            var targetType2 = typeof(Microsoft.SemanticKernel.ProcessBuilder).Assembly.GetType("Microsoft.SemanticKernel.ProcessFunctionTarget");
            if (targetType2 != null)
            {
                Console.WriteLine("\nType: Microsoft.SemanticKernel.ProcessFunctionTarget (Found!)");
            }
            else
            {
                Console.WriteLine("\nType: Microsoft.SemanticKernel.ProcessFunctionTarget (Not Found)");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            // If type not found, try to list all types in the assembly of a known type
            try {
                var known = typeof(Kernel).Assembly; // Main SK assembly
                Console.WriteLine($"\nScanning {known.FullName} for 'Process' types...");
                foreach(var t in known.GetTypes().Where(t => t.Name.Contains("Process")))
                {
                   Console.WriteLine(t.FullName);
                }
            } catch {}
        }
    }
}
