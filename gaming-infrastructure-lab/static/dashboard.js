"use strict";
const byId = id => document.getElementById(id);
const node = (tag, text, cls) => {
  const e = document.createElement(tag);
  if (text !== undefined) e.textContent = text;
  if (cls) e.className = cls;
  return e;
};
let active = null;
async function jsonRequest(path, options) {
  const response = await fetch(path, {cache: "no-store", ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function edit(type, item) {
  active = {type, item};
  const isAlert = type === "alerts";
  const next = isAlert ? (item.state === "open" ? "triaged" : "closed") :
    (item.state === "open" ? "remediated" : "verified");
  active.next = next;
  byId("editor-title").textContent = next === "triaged" ? "Triage alert" :
    next === "closed" ? "Close alert" : next === "remediated" ? "Record remediation" : "Verify remediation";
  byId("notes-label").textContent = next === "verified" ? "Rescan or verification evidence" :
    next === "remediated" ? "Change made or proposed in the simulation" :
    "Assessment, action and escalation notes";
  byId("notes").value = "";
  byId("form-error").textContent = "";
  byId("level-field").hidden = !(isAlert && next === "triaged");
  byId("level").value = item.severity;
  byId("editor").showModal();
}
function renderList(target, rows, type) {
  target.replaceChildren();
  if (!rows.length) target.append(node("p", "No records yet. Run python tools/lab.py demo to add synthetic events.", "empty"));
  rows.forEach(item => {
    const row = node("article", undefined, "record");
    const details = node("div");
    details.append(node("strong", item.summary), node("p", (item.source || item.asset) + " | " + item.created_at),
      node("span", item.severity + " / " + item.state, "status " + item.severity + " " + item.state));
    const notes = item.notes || [item.remediation, item.verification].filter(Boolean).join("\n");
    if (notes) details.append(node("p", notes, "notes"));
    row.append(details);
    if (!["closed","verified"].includes(item.state)) {
      const button = node("button", item.state === "open" ? (type === "alerts" ? "Triage" : "Remediate") :
        (type === "alerts" ? "Close" : "Verify"));
      button.type = "button";
      button.addEventListener("click", () => edit(type,item));
      row.append(button);
    }
    target.append(row);
  });
}
async function refresh() {
  try {
    const data = await jsonRequest("/api/status");
    byId("connection").textContent = "Connected | Updated " + new Date().toLocaleTimeString();
    byId("online").textContent = data.sites.filter(s => s.status === "online").length + "/" + data.sites.length;
    byId("alerts").textContent = data.open_alerts;
    byId("findings").textContent = data.open_findings;
    byId("sites").replaceChildren();
    data.sites.forEach(site => {
      const box = node("article", undefined, "site");
      box.append(node("span", site.status, "status " + site.status), node("strong", site.name),
        node("small", site.age_seconds === null ? "No heartbeat received" : "Last heartbeat " + site.age_seconds + "s ago"));
      byId("sites").append(box);
    });
    renderList(byId("alert-list"), data.alerts, "alerts");
    renderList(byId("finding-list"), data.findings, "findings");
  } catch (err) {
    byId("connection").textContent = "Unavailable | " + err.message;
  }
}
byId("refresh").addEventListener("click", refresh);
byId("cancel").addEventListener("click", () => byId("editor").close());
byId("edit-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (!active) return;
  const {type,item,next} = active;
  const notes = byId("notes").value.trim();
  const body = {state: next};
  if (type === "alerts") {
    body.notes = notes;
    if (next === "triaged") body.severity = byId("level").value;
  } else body[next === "verified" ? "verification" : "remediation"] = notes;
  try {
    await jsonRequest("/api/" + type + "/" + item.id, {method:"PATCH",
      headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    byId("editor").close();
    active = null;
    await refresh();
  } catch (err) { byId("form-error").textContent = err.message; }
});
refresh();
setInterval(refresh,5000);
