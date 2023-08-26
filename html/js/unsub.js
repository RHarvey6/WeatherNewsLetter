function unsub(params){

    if (Object.keys(params).length > 1) {
        fetch("https://formsubmit.co/faa81bd436bb81c7b8a89ee0b0bcad48", {
          method: "POST",
          headers: {'Content-Type': 'unsub/json'}, 
          body: JSON.stringify(params)
        }).then(res => {
          console.log("Request complete! response:", res);
        });
    }
    else{
        console.log("failed to post")
        console.log(params)

    }
};

window.onload = function() {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);
  
    urlParams = {};
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
    console.log(urlParams)
    unsub(urlParams)
};
