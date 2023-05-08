from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import io
import cgi
from molsql import Database
import MolDisplay
import molecule as ml
import html

#converts malicious chars so that HTML tags are displayed as plain text
def sanitize_input(input_str):
    return html.escape(input_str)

class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def rotation_script(self):
        return '''
            <script>
                let currentRotation = 0;
                const rotateSVG = (deg) => {
                    currentRotation += deg;
                    const svgElement = document.querySelector("#molecule-svg");
                    svgElement.setAttribute("transform", `rotate(${currentRotation})`);
                }
            </script>
        '''

    def do_GET(self):
        # The css style for each html page
        lookGood = '''
            a {
                
                background-color: black;
                box-shadow: 0 5px 0 darkred;
                color: white;
                padding: 1em 1.5em;
                position: relative;
                text-decoration: none;
                text-transform: uppercase;
                z-index: 1000;
            }
            form {
                margin-top: 50px;
                font-family: Arial, sans-serif;
                background-color: #f1f1f1;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
                max-width: 500px;
                margin: 50px auto;
            }
            label {display: block;margin-bottom: 5px;}
            input[type="text"], select {
                width: 100%;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 3px;
                margin-bottom: 20px;
            }
            input[type="submit"] {
                width: 100%;
                background-color: darkred;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin-bottom: 10px;
            }
            input[type="submit"]:hover {background-color: black;}
            #button-container {position: absolute; top: 60px; left: 10px; z-index: 1000;}
            input[type="file"] {font-size: 14px;padding: 10px;margin-bottom: 20px;}
        '''

        if self.path == "/":
            db = Database()
            molecules = db.get_all_molecules()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html>")
            self.wfile.write(b"<style>")
            self.wfile.write(lookGood.encode())
            self.wfile.write(b"</style>")
            self.wfile.write(b"<body>")
            self.wfile.write(
                b"<a href='/upload'>Upload Molecule</a> | <a href='/'>Select Molecule</a>")

            self.wfile.write(b"<html><body>")

            # Display the list of molecules
            self.wfile.write(b"<form method='POST'>")
            self.wfile.write(
                b"<label for='molecule_id'>Choose a molecule:</label>")
            self.wfile.write(b"<select name='molecule_name' id='molecule_id'>")

            for molecule in molecules:
                self.wfile.write(
                    (f"<option value='{molecule[1]}'>{molecule[1]} - {molecule[2]} atoms, {molecule[3]} bonds</option>").encode())

            self.wfile.write(b"</select>")
            self.wfile.write(b"<br><input type='submit' value='Select'>")
            self.wfile.write(b"</form>")
            self.wfile.write(b"</body></html>")

        elif self.path.startswith("/display"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            query_string = self.path.split('?', 1)[1]
            query_params = parse_qs(query_string)
            molecule_name = sanitize_input(query_params['molecule_name'][0])
            print(molecule_name)  # test
            db = Database()
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()
            molecule = db.load_mol(molecule_name)
            # mx = ml.mx_wrapper(90,0,0);
            # MolDisplay.Molecule().xform( mx.xform_matrix );
            svg_data = molecule.svg()

            self.wfile.write(b"<html><head>")
            self.wfile.write(b"<style>")
            self.wfile.write(lookGood.encode())
            self.wfile.write(b"</style>")
            self.wfile.write(self.rotation_script().encode()
                             )  # rotation script
            self.wfile.write(b"<html>")
            self.wfile.write(b"<style>")
            self.wfile.write(
                b"a { background-color: black; box-shadow: 0 5px 0 darkred; color: white; padding: 1em 1.5em; position: relative; text-decoration: none; text-transform: uppercase; }")
            self.wfile.write(b"</style>")
            self.wfile.write(b"<body>")
            self.wfile.write(
                b"<a href='/upload'>Upload Molecule</a> | <a href='/'>Select Molecule</a>")

            self.wfile.write(b"<div id='button-container'>")
            # rotate left button
            self.wfile.write(
                b"<button onclick='rotateSVG(-10)'>Rotate left</button>")
            # rotate right button
            self.wfile.write(
                b"<button onclick='rotateSVG(10)'>Rotate right</button>")
            self.wfile.write(B"</div>")
            self.wfile.write(b"<br><br>")
            # Wrap the SVG in a container
            self.wfile.write(
                b"<svg id='molecule-svg' width='1200' height='1200'>")
            self.wfile.write(svg_data.encode())
            self.wfile.write(b"</svg>")
            self.wfile.write(b"</body></html>")

        elif self.path == "/upload":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(b"<html>")
            self.wfile.write(b"<style>")
            self.wfile.write(lookGood.encode())
            self.wfile.write(b"</style>")
            self.wfile.write(b"<body>")
            self.wfile.write(
                b"<a href='/upload'>Upload Molecule</a> | <a href='/'>Select Molecule</a>")
            self.wfile.write(b"<h2>Upload Molecule</h2>")
            self.wfile.write(
                b"<form method='POST' enctype='multipart/form-data'>")
            self.wfile.write(
                b"<input type='file' name='sdf_file' accept='.sdf'>")
            self.wfile.write(
                b"<br><input type='text' name='molecule_name' placeholder='Molecule Name'>")
            self.wfile.write(b"<br><input type='submit' value='Upload'>")
            self.wfile.write(b"</form>")
            self.wfile.write(b"</body></html>")

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type']},
            )

            molecule_name = form['molecule_name'].value
            self.send_response(303)
            self.send_header(
                "Location", f"/display?molecule_name={molecule_name}")
            self.end_headers()

        if self.path == "/upload":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type']},
            )

            sdf_file = form['sdf_file'].file
            sdf_file_text_io_wrapper = io.TextIOWrapper(sdf_file)
            molecule_name = sanitize_input(form['molecule_name'].value)

            if not sdf_file or not molecule_name:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"Both sdf file and molecule name are required.")
                return

            db = Database()

            try:
                db.add_molecule(molecule_name, sdf_file_text_io_wrapper)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"An error occurred while processing the sdf file.")
                print(f"Error: {e}")
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body>")
            self.wfile.write(b"Molecule uploaded successfully.")
            self.wfile.write(b"<br><a href='/'>Return to homepage</a>")
            self.wfile.write(b"</body></html>")

        else:
            self.send_error(404, "Not Found")


if __name__ == "__main__":
    server_address = ("", 57237)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print("Serving on port 57237")
    httpd.serve_forever()

