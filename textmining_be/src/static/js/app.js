// console.log("JS LOADED");

// let allData = [];
// let chart;

// const dummyData = [
//   {
//     username: "user_1",
//     text: "Komentar tidak pantas",
//     prediction: "Pelanggaran Seksual",
//   },
//   {
//     username: "user_2",
//     text: "Komentar aman",
//     prediction: "Non Pelecehan Seksual",
//   },
//   {
//     username: "user_3",
//     text: "Ucapan vulgar",
//     prediction: "Pelanggaran Seksual",
//   },
//   {
//     username: "user_4",
//     text: "Komentar biasa saja",
//     prediction: "Non Pelecehan Seksual",
//   },
// ];

// function detectDummy() {
//   console.log("DUMMY CLICKED");

//   allData = dummyData;
//   showResult();
//   updateChart(dummyData);
//   renderTable(dummyData);
// }

// function updateChart(data) {
//   const sexual = data.filter(
//     (d) => d.prediction === "Pelanggaran Seksual"
//   ).length;

//   const nonSexual = data.filter(
//     (d) => d.prediction === "Non Pelecehan Seksual"
//   ).length;

//   const sexualPercent = ((sexual / data.length) * 100).toFixed(1);
//   const nonSexualPercent = ((nonSexual / data.length) * 100).toFixed(1);

//   const ctx = document.getElementById("resultChart");

//   if (chart) chart.destroy();

//   chart = new Chart(ctx, {
//     type: "bar", // ⬅ BAR CHART
//     data: {
//       labels: [
//         "Pelanggaran Pelecehan Seksual",
//         "Pelanggaran Non Pelecehan Seksual",
//       ],
//       datasets: [
//         {
//           label: "Persentase (%)",
//           data: [sexualPercent, nonSexualPercent],
//           backgroundColor: ["#1f77b4", "#4da3ff"],
//           borderRadius: 6,
//           barThickness: 45,
//         },
//       ],
//     },
//     options: {
//       responsive: true,
//       maintainAspectRatio: true,
//       aspectRatio: 2,

//       // ⬇️ INI YANG MENENTUKAN ARAH BAR
//       indexAxis: "y", // ⬅ VERTICAL (boleh dihapus, default-nya 'x')

//       scales: {
//         y: {
//           beginAtZero: true,
//           max: 100,
//           ticks: {
//             callback: (value) => value + "%",
//           },
//           title: {
//             display: true,
//             text: "Persentase",
//           },
//         },
//         x: {
//           title: {
//             display: true,
//             text: "Kategori Pelanggaran",
//           },
//           grid: {
//             display: false,
//           },
//         },
//       },
//       plugins: {
//         legend: {
//           display: false,
//         },
//       },
//     },
//   });
// }

// function renderTable(data) {
//   const tbody = document.getElementById("resultTable");
//   tbody.innerHTML = "";

//   data.forEach((d) => {
//     tbody.innerHTML += `
//       <tr>
//         <td>${d.username}</td>
//         <td>${d.text}</td>
//         <td><span class="badge">${d.prediction}</span></td>
//       </tr>
//     `;
//   });
// }

// function filterData(category) {
//   const filtered = allData.filter((d) => d.prediction === category);
//   renderTable(filtered);
// }

// function showResult() {
//   document.getElementById("emptyChart").style.display = "none";
//   document.getElementById("emptyTable").style.display = "none";

//   document.getElementById("resultChart").style.display = "block";
//   document.getElementById("resultTableWrapper").style.display = "table";
// }

// function detect() {
//   const url = document.getElementById("videoUrl").value;

//   fetch("/detect", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ video_url: url }),
//   })
//     .then((res) => res.json())
//     .then((data) => {
//       allData = data;
//       updateChart(data);
//       renderTable(data);
//     });
// }

// function updateChart(data) {
//   const sexual = data.filter(
//     (d) => d.prediction === "Pelanggaran Seksual"
//   ).length;
//   const nonSexual = data.length - sexual;

//   const ctx = document.getElementById("resultChart");

//   if (chart) chart.destroy();

//   chart = new Chart(ctx, {
//     type: "bar",
//     data: {
//       labels: ["Pelanggaran Seksual", "Non Pelecehan Seksual"],
//       datasets: [
//         {
//           data: [
//             ((sexual / data.length) * 100).toFixed(1),
//             ((nonSexual / data.length) * 100).toFixed(1),
//           ],
//         },
//       ],
//     },
//   });
// }

// function renderTable(data) {
//   const tbody = document.getElementById("resultTable");
//   tbody.innerHTML = "";

//   data.forEach((d) => {
//     tbody.innerHTML += `
//             <tr>
//                 <td>${d.username}</td>
//                 <td>${d.text}</td>
//                 <td><span class="badge">${d.prediction}</span></td>
//             </tr>
//         `;
//   });
// }

// function filterData(category) {
//   const filtered = allData.filter((d) => d.prediction === category);
//   renderTable(filtered);
// }

console.log("JS LOADED");

let allData = [];
let currentPage = 1;
const rowsPerPage = 30;

let chart;

// ===============================
// HELPER: SET LOADING BUTTON
// ===============================
function setLoading(isLoading) {
  const btn = document.getElementById("checkBtn");

  if (isLoading) {
    btn.disabled = true;
    btn.innerText = "Processing...";
  } else {
    btn.disabled = false;
    btn.innerText = "check";
  }
}

// ===============================
// FUNGSI DETECT
// ===============================
function detect() {
  const url = document.getElementById("videoUrl").value;

  if (!url) {
    Swal.fire({
      icon: "warning",
      title: "Oops!",
      text: "Masukkan link video terlebih dahulu.",
    });
    return;
  }

  // 🔥 Loading SweetAlert
  Swal.fire({
    title: "Sedang menganalisis...",
    text: "Mohon tunggu, komentar sedang diproses",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  fetch("/detect", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ video_url: url }),
  })
    .then((res) => res.json())
    .then((data) => {
      allData = data;
      currentPage = 1;

      showResult();
      updateChart(data);
      renderTable(data);

      // ✅ Tutup loading
      Swal.close();
    })
    .catch((err) => {
      console.error(err);

      Swal.fire({
        icon: "error",
        title: "Gagal",
        text: "Terjadi kesalahan saat memproses data.",
      });
    });
}

// ===============================
// UPDATE CHART (AMAN)
// ===============================
function updateChart(data) {
  if (!data || data.length === 0) return;

  const sexual = data.filter(
    (d) => d.prediction === "Pelanggaran Seksual"
  ).length;

  const nonSexual = data.length - sexual;

  const sexualPercent = ((sexual / data.length) * 100).toFixed(1);
  const nonSexualPercent = ((nonSexual / data.length) * 100).toFixed(1);

  const ctx = document.getElementById("resultChart");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Pelanggaran Seksual", "Non Pelanggaran Pelecehan Seksual"],
      datasets: [
        {
          label: "Persentase (%)",
          data: [sexualPercent, nonSexualPercent],
          backgroundColor: ["#1f77b4", "#4da3ff"],
          borderRadius: 6,
          barThickness: 45,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      indexAxis: "y",
      scales: {
        x: {
          max: 100,
          ticks: {
            callback: (value) => value + "%",
          },
          title: {
            display: true,
            text: "Persentase",
          },
          grid: {
            display: false,
          },
        },
        y: {
          title: {
            display: true,
            text: "Kategori Pelanggaran",
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
}

// ===============================
// RENDER TABLE
// ===============================
function renderTable(data) {
  const tbody = document.getElementById("resultTable");
  tbody.innerHTML = "";

  const start = (currentPage - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  const pageData = data.slice(start, end);

  pageData.forEach((d) => {
    tbody.innerHTML += `
      <tr>
        <td>${d.username || "-"}</td>
        <td>${d.text || "-"}</td>
        <td><span class="badge">${d.prediction || "-"}</span></td>
      </tr>
    `;
  });

  renderPagination(data.length);
}

function renderPagination(totalRows) {
  const pagination = document.getElementById("pagination");
  const pageInfo = document.getElementById("pageInfo");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  const totalPages = Math.ceil(totalRows / rowsPerPage);

  pagination.style.display = totalPages > 1 ? "flex" : "none";
  pageInfo.innerText = `Page ${currentPage} of ${totalPages}`;

  prevBtn.disabled = currentPage === 1;
  nextBtn.disabled = currentPage === totalPages;

  prevBtn.onclick = () => {
    if (currentPage > 1) {
      currentPage--;
      renderTable(allData);
    }
  };

  nextBtn.onclick = () => {
    if (currentPage < totalPages) {
      currentPage++;
      renderTable(allData);
    }
  };
}

// ===============================
// SHOW RESULT
// ===============================
function showResult() {
  document.getElementById("emptyChart").style.display = "none";
  document.getElementById("emptyTable").style.display = "none";

  document.getElementById("resultChart").style.display = "block";
  document.getElementById("resultTableWrapper").style.display = "table";
}
