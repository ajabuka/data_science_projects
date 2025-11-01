// Portion of this codes are sources from d3-graph gallery
const width = 1000
const height = 550
const svg=d3.select('.map')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            // .attr("style", 'border: 3px solid blue');

// Map and projection
const projection = d3.geoMercator()
    .center([11, 9.5])    // GPS of location to zoom on
    .scale(3000)        // Zoom map

// Load external data and shapefile
Promise.all([
    d3.json("nigeria_state_boundaries.geojson"),
    d3.csv("Map_Data.csv")
])
.then(function([geoJson, csvData]) {
    // Convert CSV data into a Map for easy lookup
    const data = new Map();
    csvData.forEach(d => {
        data.set(d.admin1Name, { 
            Total: +d.Total, 
            Fraud: +d.TRUE,
            Percentage: +d.Percentage
        });
    });

    buildMap(geoJson, data, metric="Total");

    // Listen for dropdown changes
    d3.select("#metric").on("change", function () {
        const selectedMetric = this.value;
        buildMap(geoJson, data, selectedMetric);
    });

// to catch error arising
}).catch(function (error) {
    d3.select('.error')
        .style('visibility', 'visible')
        .text("Error loading data: " + error);
});

// Function to dynamically create a color scale for a metric
function getColorScale(metric, data) {
    // Get min/max values of the selected metric
    const values = Array.from(data.values()).map(d => d[metric]);
    const minValue = d3.min(values);
    const maxValue = d3.max(values);

    // Create a dynamic domain range
    const step = (maxValue - minValue) / 5;
    const dynamicDomain = d3.range(minValue, maxValue, step);

    // Declare color scales dynamically
    const colorScales = {
        Total: d3.scaleThreshold().domain(dynamicDomain).range(d3.schemeBlues[7]), // Blue
        Fraud: d3.scaleThreshold().domain(dynamicDomain).range(d3.schemeOranges[7]),  // Orange
        Percentage: d3.scaleThreshold().domain(dynamicDomain).range(d3.schemeReds[7])  // Red
    };

    return colorScales[metric];
}

function maxValue(metric, data) {
    // Get min/max values of the selected metric
    const values = Array.from(data.values()).map(d => d[metric]);
    const maxValue = d3.max(values);

    return maxValue[metric];
}

// Function to get where to write state names on the map
function transformText() {
    const thisPath = d3.select(this);
    const centroid = d3.geoPath().projection(projection).centroid(thisPath.datum());

    return `translate(${centroid[0]-20}, ${centroid[1]})`;
}

// Building the Map on SVG
function buildMap(geoJson, data, metric) {

    console.log("Data = ", data);

    console.log(`Building map for: ${metric}`);

    // Get color scale for selected metric
    const colorScale = getColorScale(metric, data);

    // Tooltip
    const tooltip = d3.select(".tooltip");

    // Draw the map
    svg.append("g")
        .selectAll("path")
        .data(geoJson.features)
        .join("path")
            .attr("d", d3.geoPath()
            .projection(projection)
            )
            .attr("fill", d => {
                const value = data.get(d.properties.admin1Name)?.[metric] || 0;
                return colorScale(value);
            })
            .style("stroke", "white")
            .on("mouseover", function(event, d) {
                const value = data.get(d.properties.admin1Name)?.[metric] || 0;
                tooltip
                    .style("display", "block")
                    .html(`State: ${d.properties.admin1Name} <br> Transaction: ${value}`)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY + 10) + "px");
            })
            .on("mouseout", function() {
                tooltip.style("display", "none");
            });

    // Add the top 5 table inside the SVG at bottom-right
    updateTop5Table(svg, data, metric, width, height);

    function updateTop5Table(svg, data, metric, width, height) {
    const sortedData = Array.from(data.entries())
        .map(([admin1Name, values]) => ({ admin1Name, value: values[metric] }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5);

    // Remove old table
    svg.selectAll("foreignObject").remove();

    // Add new table
    const tableContainer = svg.append("foreignObject")
        .attr("x", width - 310)  // Positioned at bottom-right
        .attr("y", height - 220)
        .attr("width", 300)
        .attr("height", 200);

    const table = tableContainer.append("xhtml:table");

    table.append("thead").append("tr")
        .html("<th>State</th><th>Value</th>");

    const tbody = table.append("tbody");

    sortedData.forEach(d => {
        tbody.append("tr")
            .html(`<td>${d.admin1Name}</td><td>${d.value}</td>`);
    });

}

// Draw the color scale legend inside SVG
drawLegend(svg, metric, colorScale, width, height);

// Function to update the legend dynamically
function drawLegend(svg, metric, colorScale, width, height) {
    const legendWidth = 20, legendHeight = 200;

    // Remove previous legend
    svg.selectAll(".legend").remove();

    // Get domain values for the legend
    let legendValues = colorScale.domain();

    // Compute true max value from the full data for the selected metric
    const allValues = Array.from(data.values()).map(d => d[metric]);
    const trueMaxValue = d3.max(allValues);

    // Append the true max value to the legend values
    legend_Values = [...legendValues, trueMaxValue];
    console.log(legendValues)

    // Append legend group
    const legendGroup = svg.append("g")
        .attr("class", "legend")
        .attr("transform", `translate(${width - legendWidth - 150}, ${height - 500})`);

    // Draw the legend color blocks
    legendGroup.selectAll("rect")
        .data(legendValues)
        .enter().append("rect")
        .attr("x", 20)
        .attr("y", (d, i) => i * (legendHeight / (legendValues.length + 1)))
        .attr("width", legendWidth)
        .attr("height", legendHeight / (legendValues.length + 1))
        .style("fill", d => colorScale(d))
        //.style("stroke", "#000");

    // Add text labels for the scale
    legendGroup.selectAll("text")
        .data(legend_Values)
        .enter().append("text")
        .attr("x", legendWidth + 20)
        .attr("y", (d, i) => i * (legendHeight / legend_Values.length) + 5)
        .attr("font-size", "15px")
        .text(d => Math.round(d));
}
}



