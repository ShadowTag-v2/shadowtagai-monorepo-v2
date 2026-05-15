/**
 * Code Refactorer Agent - TypeScript Example
 *
 * This example demonstrates how to use the Code Refactorer agent
 * to improve code quality, readability, and maintainability.
 */

import {
  analyzeCode,
  type RefactorConfig,
  refactorCode,
  refactorInteractive,
} from '../src/code-refactorer';

// Example 1: Basic code refactoring
async function basicRefactorExample() {
  console.log('=== Example 1: Basic Refactoring ===\n');

  const messyCode = `
function calc(a,b,c) {
  var result = 0;
  if(a>0) {
    if(b>0) {
      if(c>0) {
        result = a+b+c
      } else {
        result = a+b
      }
    } else {
      result = a
    }
  }
  return result
}

// TODO: fix this later
var data = [1,2,3,4,5]
for(var i=0;i<data.length;i++) {
  console.log(data[i])
}
`;

  const result = await refactorCode(messyCode, {
    language: 'javascript',
    focus: ['readability', 'best-practices'],
    aggressiveness: 'moderate',
  });

  console.log('Original Code:');
  console.log(messyCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Refactored Code:');
  console.log(result.refactoredCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Summary:');
  console.log(result.summary);
}

// Example 2: Code analysis only
async function analyzeCodeExample() {
  console.log('\n\n=== Example 2: Code Analysis ===\n');

  const problematicCode = `
function processUserData(user) {
  // FIXME: Add validation
  var userName = user.name
  var userAge = user.age
  var userEmail = user.email

  if(userName != null && userName != undefined && userName != '') {
    if(userAge != null && userAge != undefined && userAge > 0) {
      if(userEmail != null && userEmail != undefined && userEmail.includes('@')) {
        return {
          name: userName,
          age: userAge,
          email: userEmail
        }
      }
    }
  }
  return null
}
`;

  const analysis = await analyzeCode(problematicCode, 'javascript');

  console.log('Code to Analyze:');
  console.log(problematicCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Analysis Results:');
  console.log(JSON.stringify(analysis, null, 2));
}

// Example 3: Performance-focused refactoring
async function performanceRefactorExample() {
  console.log('\n\n=== Example 3: Performance Optimization ===\n');

  const slowCode = `
function findDuplicates(arr) {
  var duplicates = []
  for(var i = 0; i < arr.length; i++) {
    for(var j = i + 1; j < arr.length; j++) {
      if(arr[i] === arr[j]) {
        if(duplicates.indexOf(arr[i]) === -1) {
          duplicates.push(arr[i])
        }
      }
    }
  }
  return duplicates
}

function processItems(items) {
  var result = []
  for(var i = 0; i < items.length; i++) {
    var item = items[i]
    var processed = {
      id: item.id,
      name: item.name.toUpperCase(),
      timestamp: new Date().toISOString()
    }
    result.push(processed)
  }
  return result
}
`;

  const config: RefactorConfig = {
    language: 'javascript',
    focus: ['performance', 'best-practices'],
    aggressiveness: 'aggressive',
    explainChanges: true,
  };

  const result = await refactorCode(slowCode, config);

  console.log('Original Code:');
  console.log(slowCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Optimized Code:');
  console.log(result.refactoredCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Optimization Summary:');
  console.log(result.summary);
}

// Example 4: Custom style guide refactoring
async function styleGuideRefactorExample() {
  console.log('\n\n=== Example 4: Style Guide Enforcement ===\n');

  const unstyledCode = `
const processdata = (input)=>{
  let Output=[];
  for(let Item of input){
    const NEW_ITEM={...Item,processed:true};
    Output.push(NEW_ITEM);
  }
  return Output;
};

class dataProcessor {
  constructor(config) {
    this.Config=config;
  }

  Process(data) {
    return data.map(item=>({
      ...item,
      timestamp:Date.now()
    }));
  }
}
`;

  const result = await refactorCode(unstyledCode, {
    language: 'typescript',
    focus: ['readability', 'best-practices'],
    styleGuide: 'Airbnb JavaScript Style Guide',
    aggressiveness: 'moderate',
  });

  console.log('Original Code:');
  console.log(unstyledCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Styled Code:');
  console.log(result.refactoredCode);
}

// Example 5: Interactive refactoring session
async function interactiveRefactorExample() {
  console.log('\n\n=== Example 5: Interactive Refactoring ===\n');

  const codeToRefactor = `
function calculateTotal(items) {
  var total = 0
  var tax = 0
  var discount = 0

  for(var i = 0; i < items.length; i++) {
    total = total + items[i].price * items[i].quantity
  }

  if(total > 100) {
    discount = total * 0.1
  }

  tax = (total - discount) * 0.08

  return total - discount + tax
}
`;

  console.log('Starting interactive refactoring session...');
  console.log('(In a real application, you would interact with the user here)');

  const session = refactorInteractive(codeToRefactor, {
    language: 'javascript',
    focus: ['readability', 'maintainability'],
    explainChanges: true,
  });

  // Collect initial response
  let done = false;
  while (!done) {
    const { value, done: isDone } = await session.next();
    if (isDone) break;

    if (value) {
      console.log(value);
    }

    // In a real application, you would get user input here
    // For this example, we'll just end after the first response
    done = true;
    await session.next('done');
  }
}

// Example 6: Addressing specific issues
async function specificIssuesExample() {
  console.log('\n\n=== Example 6: Addressing Specific Issues ===\n');

  const buggyCode = `
function divide(a, b) {
  return a / b
}

function getUserData(userId) {
  const response = fetch('https://api.example.com/users/' + userId)
  return response.json()
}

function saveToLocalStorage(key, value) {
  localStorage.setItem(key, value)
}
`;

  const result = await refactorCode(buggyCode, {
    language: 'javascript',
    specificIssues: [
      'Add error handling',
      'Make async functions properly use async/await',
      'Add input validation',
      'Add try/catch blocks',
    ],
    explainChanges: true,
  });

  console.log('Original Code:');
  console.log(buggyCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Fixed Code:');
  console.log(result.refactoredCode);
  console.log(`\n${'='.repeat(50)}\n`);
  console.log('Fixes Applied:');
  console.log(result.summary);
}

// Main execution
async function main() {
  console.log('Code Refactorer Agent - Examples\n');
  console.log('=' * 60);

  try {
    // Run all examples
    await basicRefactorExample();
    await analyzeCodeExample();
    await performanceRefactorExample();
    await styleGuideRefactorExample();
    await interactiveRefactorExample();
    await specificIssuesExample();

    console.log('\n\n✅ All examples completed successfully!');
  } catch (_error) {
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export {
  analyzeCodeExample,
  basicRefactorExample,
  interactiveRefactorExample,
  performanceRefactorExample,
  specificIssuesExample,
  styleGuideRefactorExample,
};
