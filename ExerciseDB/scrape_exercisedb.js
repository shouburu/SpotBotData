const fs = require('fs');

const API_KEY = '4cfa903c09msh176b5fbfe2ea998p1af36bjsn9b6d46da9e3e';
const HOST = 'edb-with-gifs-and-images-by-ascendapi.p.rapidapi.com';
const BASE_URL = `https://${HOST}/api/v1/exercises`;

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchExercises() {
  let allExercises = [];
  let cursor = null;
  const limit = 50; // Depending on what RapidAPI allows, typically 10 to 50 for cursor pagination. Let's use 50.

  console.log(`Starting to scrape ExerciseDB...`);

  while (true) {
    console.log(`Fetching batch... (cursor: ${cursor || 'start'})`);
    const options = {
      method: 'GET',
      headers: {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': HOST
      }
    };
    
    let url = `${BASE_URL}?limit=${limit}`;
    if (cursor) {
      url += `&after=${cursor}`;
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        let errText = await response.text().catch(e => '');
        console.error(`API Error: ${response.status} ${response.statusText} - ${errText}`);
        if (response.status === 403) {
          console.error('\nNOTE: A 403 error often means the provided API_KEY is not subscribed to "EDB WITH IMAGES AND GIFS" on RapidAPI.');
          console.error('Please visit your RapidAPI dashboard, subscribe to the API, and update the API_KEY variable if necessary.\n');
        }
        break; // Stop on error
      }

      const json = await response.json();
      
      if (!json.success) {
         console.error('API responded with success: false', json);
         break;
      }

      const data = json.data || [];
      const meta = json.meta || {};
      
      const count = data.length;
      console.log(`Received ${count} exercises in this batch.`);
      
      if (count === 0) {
        console.log(`No more exercises found. We are done!`);
        break;
      }
      
      allExercises = allExercises.concat(data);
      console.log(`Total exercises fetched so far: ${allExercises.length} / ${meta.total || '?'}`);

      if (!meta.hasNextPage) {
        console.log(`hasNextPage is false. Assuming we reached the end.`);
        break;
      }

      cursor = meta.nextCursor;

      // Rate limit is 110 requests/minute (approx 1.83 req/sec)
      // To be safe, wait 1 second between requests
      await delay(1000);
      
    } catch (error) {
      console.error('Fetch failed:', error.message);
      break;
    }
  }

  // Save the result
  if (allExercises.length > 0) {
    const outputPath = './ExerciseDB/all_exercises.json';
    fs.writeFileSync(outputPath, JSON.stringify(allExercises, null, 2));
    console.log(`Completed successfully. Saved ${allExercises.length} exercises to ${outputPath}.`);
  } else {
    console.log('No exercises were fetched. File not saved.');
  }
}

fetchExercises();
