function processSuccessWord(inputString) {
    const words = inputString.split(' ');

    for (let i = 0; i < words.length; i++) {
      if (!i) {
        if (words[i].toLowerCase() === 'success' && i + 1 < words.length) {
            // Remove 'success' and capitalize the following word
            words.splice(i, 1, words[i + 1].charAt(0).toUpperCase() + words[i + 1].slice(1));
            // Remove the following word
            words.splice(i + 1, 1);
            return { success: true, result: words.join(' ') };
        }
      }
    }

    return { success: false, result: inputString };
}

// Example usage:
const inputString = 'success This is the success message.';
const { success, result } = processSuccessWord(inputString);

console.log(success); // true or false
console.log(result); // modified string or the original string

