const fs = require('fs');
const path = require('path');

function combineAndDeduplicate(filePaths) {
  const combined = [];
  
  // Read all files and combine into one array
  for (const filePath of filePaths) {
    console.log(`Reading ${filePath}...`);
    try {
      const data = fs.readFileSync(filePath, 'utf8');
      const exercises = JSON.parse(data);
      combined.push(...exercises);
    } catch (err) {
      console.error(`Error reading or parsing ${filePath}:`, err);
    }
  }

  const uniqueExercises = [];
  const duplicates = [];
  const seenNames = new Set();

  for (const exercise of combined) {
    if (!exercise || !exercise.name) {
      // If no name, just keep it or skip? Let's keep it to be safe, but warn.
      uniqueExercises.push(exercise);
      continue;
    }

    // Normalize name for comparison: lowercased and trimmed.
    const normalizedName = exercise.name.toLowerCase().trim();

    if (seenNames.has(normalizedName)) {
      duplicates.push(exercise);
    } else {
      uniqueExercises.push(exercise);
      seenNames.add(normalizedName);
    }
  }

  const outputDir = path.dirname(filePaths[0]); // Output to the same dir as the first file
  const finalCombinedPath = path.join(outputDir, 'finalCombinedExercises.json');
  const duplicatesPath = path.join(outputDir, 'duplicates.json');

  console.log(`Total exercises combined: ${combined.length}`);
  console.log(`Unique exercises: ${uniqueExercises.length}`);
  console.log(`Duplicates discarded: ${duplicates.length}`);

  // Write the results
  fs.writeFileSync(finalCombinedPath, JSON.stringify(uniqueExercises, null, 2), 'utf8');
  console.log(`Created: ${finalCombinedPath}`);

  fs.writeFileSync(duplicatesPath, JSON.stringify(duplicates, null, 2), 'utf8');
  console.log(`Created: ${duplicatesPath}`);
}

// Array of files to process
const filesToProcess = [
  path.join(__dirname, 'freeExercises.json'),
  path.join(__dirname, 'scrapedExercises.json')
];

combineAndDeduplicate(filesToProcess);
