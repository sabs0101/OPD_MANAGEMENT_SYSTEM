document.addEventListener("DOMContentLoaded",()=>{
loadPatients()
loadCounts()

document.getElementById("search").addEventListener("keyup", function(){
  const query = this.value.toLowerCase()
  const rows = document.querySelectorAll("#patientTable tr")
  rows.forEach(row => {
    row.style.display = row.innerText.toLowerCase().includes(query) ? "" : "none"
  })
})
})

function loadCounts(){

fetch("/api/counts")
.then(r=>r.json())
.then(data=>{
document.getElementById("totalPatients").innerText=data.patients
document.getElementById("doctorCount").innerText=data.doctors
document.getElementById("nurseCount").innerText=data.nurses
})
}

function loadPatients(){

fetch("/api/patients")
.then(r=>r.json())
.then(data=>{

let table=document.getElementById("patientTable")
table.innerHTML=""

const val = v => (v !== null && v !== undefined && v !== "") ? v : "—"

data.forEach(p=>{

table.innerHTML+=`
<tr>
<td>${val(p.patient_id)}</td>
<td>${val(p.name)}</td>
<td>${val(p.age)}</td>
<td>${val(p.disease)}</td>
<td>${val(p.doctor)}</td>
<td>${val(p.nurse)}</td>

<td>
<a href="/patients/edit/${p.patient_id}" class="btn btn-warning btn-sm">✏</a>
<a href="/patients/delete/${p.patient_id}" class="btn btn-danger btn-sm">🗑</a>
</td>
</tr>
`

})
})
}

