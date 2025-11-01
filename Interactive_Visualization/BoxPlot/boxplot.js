// Load and process the data
d3.csv("cleaned_transaction_data.csv").then(function(data) {
    // Convert string amounts to numbers
    data.forEach(function(d) {
        d.Transaction_Amount = +d.Transaction_Amount;
    });
    
    // Set up dimensions
    const margin = {top: 60, right: 30, bottom: 70, left: 60};
    const width = 1000 - margin.left - margin.right;
    const height = 550 - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(".boxplot")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Initialize scales
    const x = d3.scaleBand()
        .domain(["No", "Yes"])
        .range([0, width])
        .padding(0.3);
    
    const y = d3.scaleLinear()
        .range([height, 0]);
    
    // Add X axis
    const xAxis = svg.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", `translate(0,${height})`);
    
    // Add Y axis
    const yAxis = svg.append("g")
        .attr("class", "axis axis--y");
    
    // Add X axis label
    svg.append("text")
        .attr("transform", `translate(${width/2}, ${height + margin.top - 10})`)
        .style("text-anchor", "middle")
        .text("Fraud Status");
    
    // Add Y axis label
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Transaction Amount ($)");
    
    // Add chart title
    // const title = svg.append("text")
    //     .attr("x", width / 2)
    //     .attr("y", 0 - (margin.top / 2))
    //     .attr("text-anchor", "middle")
    //     .attr("class", "title");
    
    // Create tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    
    // Update function for dropdown selection
    function updateBoxplot(deviceType) {
        // Filter data based on device selection
        const filteredData = deviceType === "All" ? 
            data : 
            data.filter(d => d.Device_Used === deviceType);
        
        // Group by fraud status
        const groupedData = d3.group(filteredData, d => d.Fraud_Flag);
        
        // Calculate summary statistics for each group
        const boxplotData = Array.from(groupedData, ([key, values]) => {
            const amounts = values.map(d => d.Transaction_Amount).sort(d3.ascending);
            const q1 = d3.quantile(amounts, 0.25);
            const median = d3.quantile(amounts, 0.5);
            const q3 = d3.quantile(amounts, 0.75);
            const iqr = q3 - q1;
            const min = d3.min(amounts);
            const max = d3.max(amounts);
            
            // Find outliers (1.5 * IQR rule)
            const lowerFence = q1 - 1.5 * iqr;
            const upperFence = q3 + 1.5 * iqr;
            const outliers = amounts.filter(d => d < lowerFence || d > upperFence);
            
            return {
                key: key,
                values: amounts,
                quartiles: [q1, median, q3],
                whiskers: [Math.max(min, lowerFence), Math.min(max, upperFence)],
                outliers: outliers,
                count: values.length
            };
        }).sort((a, b) => a.key.localeCompare(b.key)); // Sort by fraud status
        
        // Update y scale domain
        y.domain([0, d3.max(boxplotData, d => d3.max(d.values)) * 1.1]);
        
        // Update axes
        xAxis.call(d3.axisBottom(x));
        yAxis.call(d3.axisLeft(y));
        
        // Update title
        document.getElementById("chart_title").innerText = 
            `Transaction Amount Distribution by Fraud Status (${deviceType === "All" ? "All Devices" : deviceType})`;
        
        // Remove existing boxplots
        svg.selectAll(".boxplot-group").remove();
        
        // Draw boxplots for each group
        const boxplotGroups = svg.selectAll(".boxplot-group")
            .data(boxplotData)
            .enter().append("g")
            .attr("class", "boxplot-group")
            .attr("transform", d => `translate(${x(d.key === "Yes" ? "Yes" : "No") + x.bandwidth()/2}, 0)`);
        
        // Draw main box
        boxplotGroups.append("rect")
            .attr("class", "box")
            .attr("x", -x.bandwidth()/3)
            .attr("y", d => y(d.quartiles[2]))
            .attr("width", x.bandwidth()*2/3)
            .attr("height", d => y(d.quartiles[0]) - y(d.quartiles[2]))
            .attr("fill", d => d.key === "Yes" ? "orange" : "green")
            .on("mouseover", function(event, d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(`<strong>Fraud Status:</strong> ${d.key}<br>
                             <strong>Device:</strong> ${deviceType === "All" ? "All" : deviceType}<br>
                             <strong>Count:</strong> ${d.count}<br>
                             <strong>Q1:</strong> $${d.quartiles[0].toFixed(2)}<br>
                             <strong>Median:</strong> $${d.quartiles[1].toFixed(2)}<br>
                             <strong>Q3:</strong> $${d.quartiles[2].toFixed(2)}<br>
                             <strong>IQR:</strong> $${(d.quartiles[2] - d.quartiles[0]).toFixed(2)}<br>
                             <strong>Range:</strong> $${d.whiskers[0].toFixed(2)}-$${d.whiskers[1].toFixed(2)}<br>
                             <strong>Outliers:</strong> ${d.outliers.length}`)
                    .style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function() {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
        
        // Draw median line
        boxplotGroups.append("line")
            .attr("class", "median")
            .attr("x1", -x.bandwidth()/3)
            .attr("x2", x.bandwidth()/3)
            .attr("y1", d => y(d.quartiles[1]))
            .attr("y2", d => y(d.quartiles[1]));
        
        // Draw whiskers
        boxplotGroups.append("line")
            .attr("class", "whisker")
            .attr("x1", 0)
            .attr("x2", 0)
            .attr("y1", d => y(d.quartiles[2]))
            .attr("y2", d => y(d.whiskers[1]));
        
        boxplotGroups.append("line")
            .attr("class", "whisker")
            .attr("x1", 0)
            .attr("x2", 0)
            .attr("y1", d => y(d.quartiles[0]))
            .attr("y2", d => y(d.whiskers[0]));
        
        // Draw whisker caps
        boxplotGroups.append("line")
            .attr("class", "whisker")
            .attr("x1", -x.bandwidth()/4)
            .attr("x2", x.bandwidth()/4)
            .attr("y1", d => y(d.whiskers[1]))
            .attr("y2", d => y(d.whiskers[1]));
        
        boxplotGroups.append("line")
            .attr("class", "whisker")
            .attr("x1", -x.bandwidth()/4)
            .attr("x2", x.bandwidth()/4)
            .attr("y1", d => y(d.whiskers[0]))
            .attr("y2", d => y(d.whiskers[0]));
        
        // Draw outliers
        boxplotGroups.selectAll(".outlier")
            .data(d => d.outliers.map(outlier => ({outlier: outlier, key: d.key})))
            .enter().append("circle")
            .attr("class", "outlier")
            .attr("cx", () => (Math.random() - 0.5) * x.bandwidth()/3)
            .attr("cy", d => y(d.outlier))
            .attr("r", 3)
            .on("mouseover", function(event, d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(`<strong>Outlier:</strong> $${d.outlier.toFixed(2)}<br>
                             <strong>Fraud Status:</strong> ${d.key}<br>
                             <strong>Device:</strong> ${deviceType === "All" ? "All" : deviceType}`)
                    .style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function() {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
    }
    
    // Initial render with all devices
    updateBoxplot("All");
    
    // Add event listener for dropdown
    d3.select("#device-select").on("change", function() {
        updateBoxplot(this.value);
    });
    
}).catch(function(error) {
    console.error("Error loading the data:", error);
});