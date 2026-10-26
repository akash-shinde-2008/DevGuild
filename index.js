import ollama from 'ollama';

async function main() {
  try {
    const response = await ollama.chat({
      model: 'gemma',
      messages: [{ role: 'user', content: 'What is Hacktoberfest?' }],
    });

    console.log(response.message.content);
  } catch (error) {
    console.error('Error connecting to Ollama:', error.message);
  }
}

main();