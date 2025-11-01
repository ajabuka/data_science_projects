// Format number with commas and 2 decimal places
function formatNumber(num) {
    return num.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
  }
  
  // set the dimensions and margins of the graph
  const margin = {top: 10, right: 100, bottom: 30, left: 30},
        width = 1000 - margin.left - margin.right,
        height = 550 - margin.top - margin.bottom;
  
  // append the svg object to the body of the page
  const svg = d3.select(".fraud_chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  
  // Create a tooltip
  const tooltip = d3.select("body")
    .append("div")
    .style("position", "absolute")
    .style("background", "lightgray")
    .style("padding", "5px")
    .style("border-radius", "5px")
    .style("visibility", "hidden")
    .style("font-size", "14px");
  
  // Read the data
  d3.csv("Dataset_Transaction_Amount.csv").then(function(data) {
  
    console.log(data)
  
    // Add "ALL" to the dropdown options
    const allGroup = ["ALL", "Fraud", "non Fraud"];
  
    d3.select("#selectButton")
      .selectAll('myOptions')
      .data(allGroup)
      .enter()
      .append('option')
      .text(d => d)
      .attr("value", d => d);
  
    const parseTime = d3.timeParse("%d/%m/%Y %H:%M");
  
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => parseTime(d.time)))
      .range([40, width]);
  
    svg.append("g")
      .attr("transform", "translate(0,480)")
      .call(d3.axisBottom(x));
  
    const maxY = d3.max(data, d => Math.max(+d["Fraud"] + +d["non Fraud"])); //  Adjust maxY to support "ALL"
  
    const y = d3.scaleLinear()
      .domain([0, maxY + 2000])
      .range([height - 30, 0]);
  
    svg.append("g")
      .attr("transform", "translate(40,0)")
      .call(d3.axisLeft(y));
  
    // Add X axis label
    svg.append("text")
      .attr("transform", `translate(${width/2}, ${height + margin.top})`)
      .style("text-anchor", "middle")
      .text("Timestamp");
  
    // Add Y axis label
    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text("Transaction Amount ($)");
  
    // Initialize line
    const line = svg.append('g').append("path")
      .datum(data)
      .attr("d", d3.line()
        .x(d => x(parseTime(d.time)))
        .y(d => y(+d.Fraud))
      )
      .attr("stroke", "black")
      .style("stroke-width", 4)
      .style("fill", "none");
  
    // Group for dots
    let dotsGroup = svg.append("g");
  
    // Update function supports "ALL"
    function update(selectedGroup) {
      const dataFilter = data.map(d => {
        const time = parseTime(d.time);
        let value;
        if (selectedGroup === "ALL") {
          value = +d["Fraud"] + +d["non Fraud"];
        } else {
          value = +d[selectedGroup];
        }
        return { time, value };
      });
  
      // Update line path
      line
        .datum(dataFilter)
        .transition()
        .duration(1000)
        .attr("d", d3.line()
          .x(d => x(d.time))
          .y(d => y(d.value))
        );
  
      const dots = dotsGroup.selectAll("circle")
        .data(dataFilter);
  
      dots.exit().remove();
  
      // Update existing dots
      dots.transition()
        .duration(1000)
        .attr("cx", d => x(d.time))
        .attr("cy", d => y(d.value))
        .style("fill", selectedGroup === "ALL" ? "steelblue" :
                       selectedGroup === "Fraud" ? "orange" :
                       "green"); 
  
      // Add new dots
      dots.enter()
        .append("circle")
        .attr("cx", d => x(d.time))
        .attr("cy", d => y(d.value))
        .attr("r", 7)
        .style("fill", selectedGroup === "Fraud" ? "orange" :
                       selectedGroup === "non Fraud" ? "green" :
                       "steelblue") 
        .on("mouseover", function(event, d) {
          tooltip.style("visibility", "visible")
            .text(`Time: ${d3.timeFormat("%d/%m/%Y %H:%M")(d.time)}, Amount: $${formatNumber(d.value)}`);
          d3.select(this).attr("r", 10);
        })
        .on("mousemove", function(event) {
          tooltip.style("top", (event.pageY - 10) + "px")
                 .style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function() {
          tooltip.style("visibility", "hidden");
          d3.select(this).attr("r", 7);
        });
    }
  
    // Initial render with "Fraud"
    update("ALL");
  
    // On dropdown change, update chart
    d3.select("#selectButton").on("change", function() {
      const selectedOption = d3.select(this).property("value");
      update(selectedOption);
    });
  
  });
  