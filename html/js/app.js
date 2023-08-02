d3.csv("uscities.csv").then(function (data) {
  // console.log(data);

  var cityStates = data;

  var button = d3.select("#selectState");

  //var form = d3.select("#form");

  button.on("change", runEnter);
  //form.on("submit", runEnter);

  console.log(cityStates)

  function runEnter() {
    alert('test')

    d3.select("output").html("") //goes to the output at end of file, will change
    d3.event.preventDefault(); //stops page refreshing
    var inputElement = d3.select("#selectState").property("value"); //Input from the state select box
    var filteredCities = cityStates.filter(cityStates => cityStates.state.include(inputElement))
    console.log(filteredCities)
    /*
    d3.select("output").html("")
    d3.event.preventDefault();
    var inputElement = d3.select("#selectState");
    var inputValue = inputElement.property("value").toLowerCase().trim();

    console.log(inputValue.length)

    // console.log(inputValue.length);
    // console.log(movies);
    /*
    if (inputValue.length < 6){
      d3.select("p").classed('noresults2', true).html("<center><strong>Please try using more than 5 characters to avoid too many results!</strong>")
      inputValue = "Something to give no results"
    }
    var filteredData = movies.filter(movies => movies.actors.toLowerCase().trim().includes(inputValue));
    // console.log(filteredData.length)
    if (filteredData.length === 0 && inputValue !== "Something to give no results"){
      d3.select("p").classed('noresults', true).html("<center><strong>No results. Please check your spelling!</strong>")
    }
    output = _.sortBy(filteredData, 'avg_vote').reverse()

    for (var i = 0; i < filteredData.length; i++) {
      // console.log(output[i]['original_title'])
      // console.log(output[i]['avg_vote'])
      // d3.select("tbody>tr>td").text(output[i]['original_title']);
      d3.select("tbody").insert("tr").html("<td>"+[i+1]+"</td>"+"<td>"+"<a href=https://www.imdb.com/title/"+output[i]['imdb_title_id']+" target='_blank'>"+(output[i]['original_title'])+"</a>"
      + "</td>" +"<td>" +(output[i]['avg_vote'])+"</td>" +"<td>" +(output[i]['year'])+"</td>"  +"<td>" +(output[i]['director'])+"</td>"+"<td>" +(output[i]['description'])+"</td>") }
      */
  };


});