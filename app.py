# app.py
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

def find_target_sites(dna, guide):
    """Find all occurrences of guide (or guide+PAM if provided) within dna (case-insensitive)."""
    dna_up = dna.upper()
    guide_up = guide.upper()
    sites = []
    start = 0
    while True:
        idx = dna_up.find(guide_up, start)
        if idx == -1:
            break
        sites.append(idx)
        start = idx + 1
    return sites

def simulate_nhej(dna, cut_index, cut_pos_relative=0):
    """
    Simulate a simple NHEJ outcome:
    - small deletion (1-5 bp) or small insertion (1-3 bp) at cut site.
    cut_index = index of guide start; cut_pos_relative = position inside guide where cut occurs.
    """
    cut_site = cut_index + cut_pos_relative
    choice = random.choice(['del', 'ins'])
    if choice == 'del':
        del_len = random.randint(1, 5)
        new_dna = dna[:cut_site] + dna[cut_site + del_len:]
        descr = f"Deletion of {del_len} base(s) at position {cut_site}."
    else:
        ins_len = random.randint(1, 3)
        bases = ''.join(random.choice('ACGT') for _ in range(ins_len))
        new_dna = dna[:cut_site] + bases + dna[cut_site:]
        descr = f"Insertion '{bases}' (length {ins_len}) at position {cut_site}."
    return new_dna, descr

def simulate_hdr(dna, cut_index, template, cut_pos_relative=0):
    """
    Simulate HDR by replacing a small region around cut with the template.
    We'll replace a region of length equal to template around the cut.
    """
    cut_site = cut_index + cut_pos_relative
    # For safety, pick a small span to replace (len(template))
    left = max(0, cut_site - (len(template)//2))
    right = min(len(dna), left + len(template))
    new_dna = dna[:left] + template.upper() + dna[right:]
    descr = f"HDR: replaced region {left}-{right} with template ({len(template)} bp)."
    return new_dna, descr

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/edit", methods=["POST"])
def edit():
    data = request.json
    dna = data.get("dna", "").strip().upper()
    guide = data.get("guide", "").strip().upper()
    method = data.get("method", "cut")
    template = data.get("template", "").strip().upper()
    cut_pos_relative = data.get("cut_pos", None)

    if not dna or not guide:
        return jsonify({"error": "DNA sequence and guide RNA are required."}), 400

    sites = find_target_sites(dna, guide)
    if not sites:
        return jsonify({"error": "Guide sequence not found in the DNA."}), 400

    # Choose first site by default (frontend can change to allow selection)
    site_index = sites[0]
    # Default cut: often 3 bases upstream of PAM for SpCas9,
    # but since we may not model PAM exactly, allow user to set cut_pos.
    if cut_pos_relative is None:
        cut_pos_relative = len(guide) - 3 if len(guide) >= 3 else len(guide)//2

    if method == "cut":
        # just indicate cut location, no sequence change
        result = {
            "method": "cut",
            "original": dna,
            "edited": dna,
            "cut_site": site_index + cut_pos_relative,
            "description": f"Cas9 cut at index {site_index + cut_pos_relative} (no repair simulated)."
        }
        return jsonify(result)
    elif method == "nhej":
        edited, descr = simulate_nhej(dna, site_index, cut_pos_relative)
        return jsonify({
            "method": "nhej",
            "original": dna,
            "edited": edited,
            "cut_site": site_index + cut_pos_relative,
            "description": descr
        })
    elif method == "hdr":
        if not template:
            return jsonify({"error": "Template sequence required for HDR simulation."}), 400
        edited, descr = simulate_hdr(dna, site_index, template, cut_pos_relative)
        return jsonify({
            "method": "hdr",
            "original": dna,
            "edited": edited,
            "cut_site": site_index + cut_pos_relative,
            "description": descr
        })
    else:
        return jsonify({"error": "Unknown method."}), 400

if __name__ == "__main__":
    app.run(debug=True)
