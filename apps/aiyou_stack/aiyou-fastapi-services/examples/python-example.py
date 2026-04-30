"""Code Refactorer Agent - Python Example

This example demonstrates how to use the Code Refactorer agent
to improve code quality, readability, and maintainability.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code_refactorer import (
    Aggressiveness,
    FocusArea,
    RefactorConfig,
    analyze_code,
    refactor_code,
    refactor_interactive,
)


async def basic_refactor_example():
    """Example 1: Basic code refactoring"""
    print("=== Example 1: Basic Refactoring ===\n")

    messy_code = """
def calc(a,b,c):
    result = 0
    if a>0:
        if b>0:
            if c>0:
                result = a+b+c
            else:
                result = a+b
        else:
            result = a
    return result

# TODO: fix this later
data = [1,2,3,4,5]
for i in range(len(data)):
    print data[i]
"""

    config = RefactorConfig(
        language="python",
        focus=[FocusArea.READABILITY, FocusArea.BEST_PRACTICES],
        aggressiveness=Aggressiveness.MODERATE,
    )

    result = await refactor_code(messy_code, config)

    print("Original Code:")
    print(messy_code)
    print("\n" + "=" * 50 + "\n")
    print("Refactored Code:")
    print(result.refactored_code)
    print("\n" + "=" * 50 + "\n")
    print("Summary:")
    print(result.summary)


async def analyze_code_example():
    """Example 2: Code analysis only"""
    print("\n\n=== Example 2: Code Analysis ===\n")

    problematic_code = """
def process_user_data(user):
    # FIXME: Add validation
    user_name = user['name']
    user_age = user['age']
    user_email = user['email']

    if user_name != None and user_name != '' and len(user_name) > 0:
        if user_age != None and user_age > 0:
            if user_email != None and '@' in user_email:
                return {
                    'name': user_name,
                    'age': user_age,
                    'email': user_email
                }
    return None
"""

    analysis = await analyze_code(problematic_code, "python")

    print("Code to Analyze:")
    print(problematic_code)
    print("\n" + "=" * 50 + "\n")
    print("Analysis Results:")
    print(f"Issues: {len(analysis.issues)}")
    for issue in analysis.issues:
        print(f"  - [{issue.severity.value.upper()}] {issue.type}: {issue.description}")
        if issue.suggestion:
            print(f"    Suggestion: {issue.suggestion}")
    print("\nMetrics:")
    print(f"  Complexity: {analysis.metrics.complexity}")
    print(f"  Maintainability Index: {analysis.metrics.maintainability_index}")
    print(f"  Technical Debt: {analysis.metrics.technical_debt}")
    print("\nRecommendations:")
    for rec in analysis.recommendations[:5]:  # Show first 5
        print(f"  - {rec}")


async def performance_refactor_example():
    """Example 3: Performance-focused refactoring"""
    print("\n\n=== Example 3: Performance Optimization ===\n")

    slow_code = """
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                if arr[i] not in duplicates:
                    duplicates.append(arr[i])
    return duplicates

def process_items(items):
    result = []
    for i in range(len(items)):
        item = items[i]
        processed = {
            'id': item['id'],
            'name': item['name'].upper(),
            'timestamp': str(datetime.now())
        }
        result.append(processed)
    return result
"""

    config = RefactorConfig(
        language="python",
        focus=[FocusArea.PERFORMANCE, FocusArea.BEST_PRACTICES],
        aggressiveness=Aggressiveness.AGGRESSIVE,
        explain_changes=True,
    )

    result = await refactor_code(slow_code, config)

    print("Original Code:")
    print(slow_code)
    print("\n" + "=" * 50 + "\n")
    print("Optimized Code:")
    print(result.refactored_code)
    print("\n" + "=" * 50 + "\n")
    print("Optimization Summary:")
    print(result.summary)


async def style_guide_refactor_example():
    """Example 4: Style guide enforcement"""
    print("\n\n=== Example 4: Style Guide Enforcement ===\n")

    unstyled_code = """
def processData(input):
    Output=[]
    for Item in input:
        NEW_ITEM={**Item,'processed':True}
        Output.append(NEW_ITEM)
    return Output

class dataProcessor:
    def __init__(self,config):
        self.Config=config

    def Process(self,data):
        return [{**item,'timestamp':time.time()} for item in data]
"""

    config = RefactorConfig(
        language="python",
        focus=[FocusArea.READABILITY, FocusArea.BEST_PRACTICES],
        style_guide="PEP 8",
        aggressiveness=Aggressiveness.MODERATE,
    )

    result = await refactor_code(unstyled_code, config)

    print("Original Code:")
    print(unstyled_code)
    print("\n" + "=" * 50 + "\n")
    print("Styled Code:")
    print(result.refactored_code)


async def interactive_refactor_example():
    """Example 5: Interactive refactoring session"""
    print("\n\n=== Example 5: Interactive Refactoring ===\n")

    code_to_refactor = """
def calculate_total(items):
    total = 0
    tax = 0
    discount = 0

    for i in range(len(items)):
        total = total + items[i]['price'] * items[i]['quantity']

    if total > 100:
        discount = total * 0.1

    tax = (total - discount) * 0.08

    return total - discount + tax
"""

    print("Starting interactive refactoring session...")
    print("(In a real application, you would interact with the user here)")

    config = RefactorConfig(
        language="python",
        focus=[FocusArea.READABILITY, FocusArea.MAINTAINABILITY],
        explain_changes=True,
    )

    session = refactor_interactive(code_to_refactor, config)

    # Collect initial response
    try:
        response = await session.asend(None)
        print(response)

        # In a real application, you would get user input here
        # For this example, we'll just end after the first response
        await session.asend("done")
    except StopAsyncIteration:
        pass


async def specific_issues_example():
    """Example 6: Addressing specific issues"""
    print("\n\n=== Example 6: Addressing Specific Issues ===\n")

    buggy_code = """
def divide(a, b):
    return a / b

def get_user_data(user_id):
    response = requests.get(f'https://api.example.com/users/{user_id}')
    return response.json()

def save_to_file(filename, data):
    f = open(filename, 'w')
    f.write(str(data))
    f.close()
"""

    config = RefactorConfig(
        language="python",
        specific_issues=[
            "Add error handling",
            "Use context managers for file operations",
            "Add input validation",
            "Add try/except blocks",
        ],
        explain_changes=True,
    )

    result = await refactor_code(buggy_code, config)

    print("Original Code:")
    print(buggy_code)
    print("\n" + "=" * 50 + "\n")
    print("Fixed Code:")
    print(result.refactored_code)
    print("\n" + "=" * 50 + "\n")
    print("Fixes Applied:")
    print(result.summary)


async def main():
    """Main execution"""
    print("Code Refactorer Agent - Examples\n")
    print("=" * 60)

    try:
        # Run all examples
        await basic_refactor_example()
        await analyze_code_example()
        await performance_refactor_example()
        await style_guide_refactor_example()
        await interactive_refactor_example()
        await specific_issues_example()

        print("\n\n✅ All examples completed successfully!")
    except Exception as error:
        print(f"❌ Error running examples: {error}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
