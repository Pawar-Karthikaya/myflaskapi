from flask import Flask, jsonify, request
import wikipedia as wk
import os

app = Flask(__name__)

def get_section(text, section_title):
    """Extracts a section from Wikipedia text based on the section title."""
    section = ''
    lines = text.splitlines()
    found_section = False

    for line in lines:
        # Check for section header, toggle the flag when found
        if line.strip().startswith("==") and section_title.lower() in line.lower():
            found_section = True
        elif line.strip().startswith("==") and found_section:
            # End of section
            break
        elif found_section:
            section += line + "\n"

    return section.strip()

@app.route('/api/wiki_info', methods=['GET'])
def wiki_info():
    # Get the input from query parameters
    apiinput = request.args.get('title', '')
    if not apiinput:
        return jsonify({"error": "Please provide a title parameter."}), 400

    try:
        # Fetch the Wikipedia page
        page = wk.page(apiinput)

        # Retrieve the content and extract relevant sections
        page_content = page.content
        data = {
            "General Information": page.summary,
            "Identification": get_section(page_content, "Description"),
            "Uses": get_section(page_content, "Uses"),
            "Medical Uses": get_section(page_content, "Traditional medicine"),
            "Location": get_section(page_content, "Distribution"),
        }
        return jsonify(data)

    except wk.DisambiguationError as e:
        return jsonify({"error": "Disambiguation error", "options": e.options}), 400
    except wk.PageError:
        return jsonify({"error": "Page not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable
    app.run(host='0.0.0.0', port=port)
