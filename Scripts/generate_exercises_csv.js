const fs = require('fs');

const rawDataPath = './ExerciseDB/all_exercises.json';
const outputPath = './exercises.csv';

function getMET(category, difficulty) {
  if (category === 'stretching') return 2.5;
  if (category === 'cardio') return 8.0;
  if (category === 'strength' || category === 'powerlifting' || category === 'strongman') {
    if (difficulty === 'beginner') return 5.0;
    if (difficulty === 'intermediate') return 6.0;
    if (difficulty === 'advanced' || difficulty === 'expert') return 8.0;
  }
  return 4.0;
}

function generateCSV() {
  const data = JSON.parse(fs.readFileSync(rawDataPath, 'utf8'));

  let csvContent = 'Name,Categories,Description,Image URL,YouTube Video URL,Muscle Fatigue Formula,Calories Burnt Formula\n';

  // Make sure to escape CSV fields correctly
  const escapeCSV = (field) => {
    if (!field) return '""';
    const str = String(field);
    return `"${str.replace(/"/g, '""')}"`;
  };

  data.forEach((ex) => {
    const name = ex.name || '';
    const category = ex.category || 'other';
    const categories = [category, ex.target, ...(ex.secondaryMuscles || [])].filter(Boolean).join(', ');
    
    // Create detailed description from instructions array or fallback to description
    const description = ex.instructions 
      ? (Array.isArray(ex.instructions) ? ex.instructions.join(' ') : ex.instructions) 
      : (ex.description || 'No description available.');

    // Construct image URL from github repo or gifUrl
    const imageUrl = ex.gifUrl ? ex.gifUrl : 
      ((ex.images && ex.images.length > 0) 
      ? `https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/${encodeURIComponent(ex.images[0])}`
      : '');

    // Construct a sample youtube search URL for proper form
    const videoUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(name + ' exercise proper form')}`;

    // Formulas
    const met = getMET(category, ex.difficulty || ex.level);
    const caloriesFormula = `Calories = (MET of ${met} * BodyWeight_in_kg * Duration_in_minutes) / 60`;
    
    let fatigueFormula = '';
    if (category === 'strength' || category === 'powerlifting') {
      fatigueFormula = `FatigueIndex = (Weight Lifted * Reps * Sets) / (Rest_Time_seconds * Target_1RM_Percentage)`;
    } else if (category === 'cardio') {
      fatigueFormula = `FatigueIndex = (Heart_Rate_avg / Heart_Rate_max) * Duration_minutes`;
    } else {
      fatigueFormula = `FatigueIndex = (Perceived_Exertion_1_to_10 / 10) * Duration_minutes`;
    }

    const row = [
      escapeCSV(name),
      escapeCSV(categories),
      escapeCSV(description),
      escapeCSV(imageUrl),
      escapeCSV(videoUrl),
      escapeCSV(fatigueFormula),
      escapeCSV(caloriesFormula)
    ].join(',');

    csvContent += row + '\n';
  });

  fs.writeFileSync(outputPath, csvContent);
  console.log(`Generated CSV with ${data.length} exercises at ${outputPath}`);
}

generateCSV();
