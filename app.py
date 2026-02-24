from flask import Flask, request, redirect, url_for, render_template_string
import csv
import io
import os

app = Flask(__name__)

assets = []
tickets = []

def normalize(h):
    return h.strip().lower().replace(" ", "").replace("/", "").replace(".", "").replace("_", "")

HOME_HTML = """
<h2>IT Help Desk</h2>
<ul>
  <li><a href="/upload">Upload Assets (CSV)</a></li>
  <li><a href="/assets">View Assets</a></li>
  <li><a href="/ticket">Create Ticket</a></li>
  <li><a href="/tickets">View Tickets</a></li>
</ul>
"""

UPLOAD_HTML = """
<h3>Upload Assets (CSV)</h3>
<form method="post" enctype="multipart/form-data">
  <input type="file" name="file" accept=".csv" required>
  <br><br>
  <button type="submit">Upload</button>
</form>
<br>
<a href="/">Back</a>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        text = file.stream.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))

        header_map = {normalize(h): h for h in reader.fieldnames}

        def get(row, key):
            return row.get(header_map.get(normalize(key), ""), "").strip()

        assets.clear()
        count = 0
        for row in reader:
            asset = {
                "asset_code": get(row, "Asset Code"),
                "sl_no": get(row, "Sl.No"),
                "location": get(row, "Location"),
                "department_user": get(row, "Department / User"),
                "device_type": get(row, "Device Type"),
                "purpose": get(row, "Purpose"),
                "person_name": get(row, "Name of the person"),
                "email": get(row, "Email Id"),
                "brand": get(row, "Brand"),
                "model": get(row, "Model"),
                "serial_number": get(row, "Serial Number"),
                "windows_version": get(row, "Windows Version"),
                "purchase_date": get(row, "Purchase Date"),
                "age": get(row, "Age"),
            }
            assets.append(asset)
            count += 1

        return f"<p>✅ {count} assets uploaded successfully.</p><a href='/assets'>View Assets</a>"

    return render_template_string(UPLOAD_HTML)

@app.route("/assets")
def list_assets():
    if not assets:
        return "<p>No assets uploaded yet.</p><a href='/'>Back</a>"

    rows = "".join(
        f"""
        <tr>
          <td>{a['asset_code']}</td>
          <td>{a['sl_no']}</td>
          <td>{a['location']}</td>
          <td>{a['department_user']}</td>
          <td>{a['device_type']}</td>
          <td>{a['purpose']}</td>
          <td>{a['person_name']}</td>
          <td>{a['email']}</td>
          <td>{a['brand']}</td>
          <td>{a['model']}</td>
          <td>{a['serial_number']}</td>
          <td>{a['windows_version']}</td>
          <td>{a['purchase_date']}</td>
          <td>{a['age']}</td>
        </tr>
        """
        for a in assets
    )

    html = f"""
    <h3>Assets</h3>
    <div style="overflow-x:auto">
    <table border="1" cellpadding="6">
      <tr>
        <th>Asset Code</th>
        <th>Sl.No</th>
        <th>Location</th>
        <th>Department / User</th>
        <th>Device Type</th>
        <th>Purpose</th>
        <th>Name</th>
        <th>Email</th>
        <th>Brand</th>
        <th>Model</th>
        <th>Serial Number</th>
        <th>Windows Version</th>
        <th>Purchase Date</th>
        <th>Age</th>
      </tr>
      {rows}
    </table>
    </div>
    <br><a href="/">Back</a>
    """
    return html

@app.route("/ticket", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        ticket = {
            "title": request.form.get("title"),
            "email": request.form.get("email"),
            "asset_code": request.form.get("asset_code"),
            "status": "Open"
        }
        tickets.append(ticket)
        return redirect(url_for("tickets_page"))

    return """
    <h3>Create Ticket</h3>
    <form method="post">
      Title: <input name="title" required><br><br>
      Email: <input name="email" required><br><br>
      Asset Code: <input name="asset_code"><br><br>
      <button type="submit">Create Ticket</button>
    </form>
    <br><a href="/">Back</a>
    """

@app.route("/tickets")
def tickets_page():
    if not tickets:
        return "<p>No tickets created yet.</p><a href='/'>Back</a>"

    rows = "".join(
        f"<tr><td>{t['title']}</td><td>{t['email']}</td><td>{t['asset_code']}</td><td>{t['status']}</td></tr>"
        for t in tickets
    )
    html = f"""
    <h3>Tickets</h3>
    <table border="1" cellpadding="6">
      <tr>
        <th>Title</th>
        <th>Email</th>
        <th>Asset Code</th>
        <th>Status</th>
      </tr>
      {rows}
    </table>
    <br><a href="/">Back</a>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
