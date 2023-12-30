document.addEventListener('DOMContentLoaded', function () {
  const element1 = document.querySelector('.new-thread');
  const element2 = document.querySelector('.most-recent-thread');

  element1.addEventListener('click', function () {
    alert("clicked");
    sendData()
    .then(responseData => {
        console.log(responseData);
      alert(JSON.stringify(responseData));
    })
    .catch(error => {
        alert(error.message);
    });
  });

  element2.addEventListener('click', function () {
    alert("clicked");
    sendData(1)
    .then(responseData => {
        console.log(responseData);
      alert(JSON.stringify(responseData));
    })
    .catch(error => {
        alert(error.message);
    });
  });


  function sendData(value = 0) {
    alert("sending data");
    const url = "/zmc_assistant_app";
    let data = {};
    const formData = new FormData();

    if (!value) {
      formData.append("thread_choice", "new_thread");
    } else {
      formData.append("thread_choice", "most_recent_thread")
    }


    return fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error('Error during fetch operation:', error);
        throw error; // Rethrow the error to handle it where the function is called
    });
  }
});

