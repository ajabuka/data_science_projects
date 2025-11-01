// --- Config and Globals ---
const tops = 8;
let Duration = 5000;
let playing = false, timer;
let currentIndex = 0;

const width = 1000;
const height = 550;
const margin = { top: 60, right: 50, bottom: 5, left: 200 };

// --- SVG and Scales Setup ---
const svg = d3.select(".barChart")
  .append("svg")
  .attr("viewBox", `0 0 ${width} ${height}`)
  .attr("preserveAspectRatio", "xMidYMid")
  .append("g");

const x = d3.scaleLinear().range([margin.left, width - margin.right]);
const y = d3.scaleBand().range([margin.top, height - 60]).padding(0.1);
// const color = d3.scaleOrdinal(d3.schemeTableau10);
const color = {
  "Cheque Deposit": "#0000FF",      // blue
  "Deposit": "#800000",             // Maroon
  "Withdrawal": "#FFC0CB",          // pink
  "Transfer": "#87CEEB",            // sky blue
  "ATM Withdrawal": "#808000",      // olive
  "Online Transfer": "#FFFF00",     // yellow
  "Bill Payment": "#00FFFF",        // cyan
  "POS Withdrawal": "#C8A2C8",      // lilac
}

const xAxis = d3.axisTop(x)
  .ticks(width > 500 ? 5 : 2)
  .tickSize(-(height - margin.top - 40))
  .tickFormat(d => `$${d3.format(",")(d)}`);

// --- Year / Time Label ---
const yearText = svg.append("text")
  .attr("class", "yearText")
  .attr("x", width - 20)
  .attr("y", height - 20)
  .style("text-anchor", "end");

// --- Tooltip ---
const tooltip = d3.select("body").append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);

// --- Load and Process Data ---
d3.csv("dataset_cleaned.csv").then(data => {
  try {
    const parseTime = d3.timeParse("%d/%m/%Y %H:%M");

    data.forEach(d => {
      d.value = +d["Transaction Amount"] || 0;
      d.timestamp = parseTime(d["Timestamp"]);
      d.type = d["Transaction Type"] || "Unknown";
      d.minute = d3.timeMinute.every(1).floor(d.timestamp);
    });

    // --- Frame Aggregation: Cumulative by 5-Minute Steps ---
    const minuteExtent = d3.extent(data, d => d.minute);
    const allMinutes = d3.timeMinute.range(minuteExtent[0], minuteExtent[1], 1);

    const frames = [];
    let cumulative = {};

    for (let minute of allMinutes) {
      const entries = data.filter(d => d.minute <= minute);
      cumulative = d3.rollups(entries, v => d3.sum(v, d => d.value), d => d.type)
        .reduce((acc, [type, value]) => {
          acc[type] = value;
          return acc;
        }, {});
      
      const frameData = Object.entries(cumulative).map(([type, value]) => ({ type, value }));
      frames.push({ minute, entries: frameData });
    }

    // Set x scale domain
    x.domain([0, d3.max(frames.flatMap(g => g.entries), d => d.value)]);

    // Add X Axis to SVG
    svg.append("g")
      .attr("class", "xAxis")
      .attr("transform", `translate(0, ${margin.top})`)
      .call(xAxis);

    // --- Render Function: Updates chart for current frame ---
    function render(frame) {
      const topData = frame.entries.sort((a, b) => b.value - a.value).slice(0, tops);
      topData.forEach((d, i) => d.rank = i);
      y.domain(d3.range(tops));
      const barHeight = y.bandwidth();

      // Update x domain and axis
      x.domain([0, d3.max(topData, d => d.value)]);
      svg.select(".xAxis")
        .transition().duration(Duration).ease(d3.easeLinear)
        .call(xAxis);

      // Bars
      const bars = svg.selectAll(".bar").data(topData, d => d.type);

      bars.enter().append("rect")
        .attr("class", "bar")
        .attr("x", x(0))
        .attr("y", d => y(d.rank))
        .attr("height", barHeight)
        .attr("width", d => x(d.value) - x(0))
        .style("fill", d => color[d.type] || "#ccc")
        .on("mouseover", (event, d) => {
          tooltip.transition().duration(200).style("opacity", .9);
          tooltip.html(`${d.type}<br/>$${d3.format(",.0f")(d.value)}`)
            .style("left", `${event.pageX + 5}px`)
            .style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", () => tooltip.transition().duration(500).style("opacity", 0))
        .merge(bars)
        .transition().duration(Duration).ease(d3.easeLinear)
        .attr("x", x(0))
        .attr("width", d => x(d.value) - x(0))
        .attr("y", d => y(d.rank));

      bars.exit().remove();

      // Type Labels
      const labels = svg.selectAll(".typeLabel").data(topData, d => d.type);

      labels.enter().append("text")
        .attr("class", "typeLabel")
        .attr("x", margin.left - 10)
        .attr("y", d => y(d.rank) + barHeight / 2 + 5)
        .attr("text-anchor", "end")
        .text(d => d.type)
        .merge(labels)
        .transition().duration(Duration).ease(d3.easeLinear)
        .attr("y", d => y(d.rank) + barHeight / 2 + 5);

      labels.exit().remove();

      // Value Labels
      const values = svg.selectAll(".valueLabel").data(topData, d => d.type);

      values.enter().append("text")
        .attr("class", "valueLabel")
        .attr("x", d => x(d.value) - 10)
        .attr("y", d => y(d.rank) + barHeight / 2 + 5)
        .attr("text-anchor", "end")
        .text(d => `$${d3.format(",.0f")(d.value)}`)
        .merge(values)
        .transition().duration(Duration).ease(d3.easeLinear)
        .attr("x", d => x(d.value) - 10)
        .attr("y", d => y(d.rank) + barHeight / 2 + 5)
        .tween("text", function(d) {
          const i = d3.interpolateNumber(+this.textContent.replace(/[^\d]/g, '') || 0, d.value);
          return t => this.textContent = `$${d3.format(",.0f")(i(t))}`;
        });

      values.exit().remove();

      // Update year/time label
      yearText.text(d3.timeFormat("%B %d, %Y - %H:%M")(frame.minute));
    }

    // --- Animation Step Handler ---
    function step() {
      if (currentIndex < frames.length - 1) {
        currentIndex++;
        render(frames[currentIndex]);
      } else {
        clearInterval(timer);
        playing = false;
        console.log("Reached end of animation.");
      }
    }

    // Initial Render
    render(frames[currentIndex]);

    // --- Controls ---
    document.getElementById("playBtn").addEventListener("click", () => {
      if (!playing) {
        playing = true;
        timer = setInterval(step, Duration);
        console.log("Animation started.");
      }
    });

    document.getElementById("pauseBtn").addEventListener("click", () => {
      clearInterval(timer);
      playing = false;
      console.log("Animation paused.");
    });

    document.getElementById("resetBtn").addEventListener("click", () => {
      clearInterval(timer);
      currentIndex = 0;
      render(frames[currentIndex]);
      playing = false;
      console.log("Animation reset.");
    });

    document.getElementById("speedSlider").addEventListener("input", (e) => {
      clearInterval(timer);
      Duration = +e.target.value;
      if (playing) timer = setInterval(step, Duration);
      console.log(`Speed updated: ${Duration} ms`);
    });
  } catch (error) {
    console.error("Error while processing data:", error);
  }
}).catch(error => {
  console.error("CSV loading failed:", error);
});
