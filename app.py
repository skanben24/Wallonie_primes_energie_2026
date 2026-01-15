# app.py - Calculateur primes Habitation Wallonie 2026 (résultats sans icônes + gains ultra mis en évidence)

from flask import Flask, render_template_string, request

app = Flask(__name__)

# Fonctions de calcul (inchangées)
def calcul_categorie_r(revenus_ref: float) -> str:
    if revenus_ref <= 25000: return 'R1'
    elif revenus_ref <= 40000: return 'R2'
    elif revenus_ref <= 60000: return 'R3'
    elif revenus_ref <= 90000: return 'R4'
    else: return 'R5'

def get_coeff_r(categorie_r: str) -> float:
    coeffs = {'R1': 6.0, 'R2': 4.0, 'R3': 3.0, 'R4': 2.0, 'R5': 1.0}
    return coeffs.get(categorie_r.upper(), 1.0)

def prime_toiture(surface: float, cat_r: str, biosource: bool) -> float:
    base = 26.0 if biosource else 20.0
    coeff = get_coeff_r(cat_r)
    prime = base * coeff * surface
    max_m2 = 156.0 if biosource else 120.0
    return round(min(prime, max_m2 * surface), 2)

def prime_murs(surface: float, cat_r: str) -> float:
    base = 8.80
    coeff = get_coeff_r(cat_r)
    prime = base * coeff * surface
    return round(min(prime, 140.0 * surface), 2)

def prime_sols(surface: float, cat_r: str) -> float:
    base = 6.0
    coeff = get_coeff_r(cat_r)
    prime = base * coeff * surface
    return round(min(prime, 132.0 * surface), 2)

def prime_pac(cat_r: str) -> float:
    montants = {'R1': 3600.0, 'R2': 3000.0, 'R3': 2400.0, 'R4': 1800.0, 'R5': 600.0}
    return montants.get(cat_r.upper(), 600.0)

def prime_ventilation(cat_r: str) -> float:
    base = 100.0
    coeff = get_coeff_r(cat_r)
    return round(base * coeff, 2)

def prime_audit(cat_r: str) -> float:
    base = 76.0
    coeff = get_coeff_r(cat_r)
    return round(base * coeff, 2)

# Template HTML – résultats sans icônes + focus sur les montants
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculateur Primes Énergie Wallonie 2026</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body {
            background: #121212;
            color: #e0e0e0;
            padding: 20px;
        }
        .container { max-width: 1000px; }
        .card {
            background: #1e1e1e;
            border: 1px solid #2ecc71;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        h1, h2, .section-title {
            color: #39ff14;
            text-shadow: 0 0 10px rgba(57,255,20,0.4);
        }
        .form-label { color: #d0d0d0; font-weight: 500; }
        .form-control, .form-select {
            background: #2c2c2c;
            color: #e0e0e0;
            border: 1px solid #444;
        }
        .form-control:focus, .form-select:focus {
            border-color: #2ecc71;
            box-shadow: 0 0 8px rgba(46,204,113,0.3);
        }
        .btn-primary {
            background: #27ae60;
            border: none;
            color: white;
            font-weight: 600;
        }
        .btn-primary:hover { background: #2ecc71; }
        .result-highlight {
            background: #1e2a1e;
            border: 1px solid #2ecc71;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .result-label {
            font-size: 1.1rem;
            color: #d0d0d0;
        }
        .money {
            font-size: 1.45rem;
            font-weight: bold;
            color: #2ecc71;
        }
        .total-block {
            text-align: center;
            padding: 25px;
            background: #1e2a1e;
            border: 2px solid #39ff14;
            border-radius: 12px;
            margin-bottom: 25px;
        }
        .total-money {
            font-size: 3.2rem;
            font-weight: 800;
            color: #39ff14;
            text-shadow: 0 0 15px rgba(57,255,20,0.6);
            margin: 0;
        }
        .total-label {
            font-size: 1.3rem;
            color: #bbb;
            margin-top: 8px;
        }
        .tips-section {
            background: #1e2a1e;
            border-left: 4px solid #27ae60;
            padding: 20px;
            margin-top: 30px;
            border-radius: 8px;
        }
        .ad-banner {
            background: #1a1a1a;
            padding: 12px;
            text-align: center;
            margin: 25px 0;
            border: 1px dashed #444;
            color: #777;
        }
        .disclaimer { font-size: 0.85rem; color: #999; text-align: center; margin-top: 30px; }
        .icon { color: #27ae60; margin-right: 8px; font-size: 1.3rem; }
        .section-title { border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="ad-banner">Emplacement pub haut</div>
        
        <h1 class="text-center mb-4">Calculateur Primes Énergie Wallonie 2026</h1>
        <p class="text-center lead mb-5" style="color: #bbb;">
            Régime transitoire jusqu'au 30/09/2026 – Agissez avant la réforme !
        </p>
        
        <div class="row">
            <div class="col-md-8">
                <form method="POST" class="card p-4">
                    <h4 class="section-title"><i class="bi bi-wallet2 icon"></i> Vos informations financières</h4>
                    <div class="mb-4">
                        <label class="form-label"><i class="bi bi-currency-euro icon"></i> Revenus de référence :</label>
                        <input type="number" name="revenus_ref" class="form-control" min="0" value="50000" required>
                    </div>

                    <h4 class="section-title"><i class="bi bi-house-door-fill icon"></i> Caractéristiques de votre maison</h4>
                    
                    <div class="mb-3">
                        <label class="form-label"><i class="bi bi-roof icon"></i> Surface toiture/combles (m²) :</label>
                        <input type="number" name="surface_toit" class="form-control" min="0" value="100">
                    </div>
                    <div class="form-check mb-4">
                        <input type="checkbox" name="biosource" class="form-check-input" id="biosource">
                        <label class="form-check-label" for="biosource"><i class="bi bi-leaf icon"></i> Isolant biosourcé (bonus)</label>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label"><i class="bi bi-bricks icon"></i> Surface murs (m²) :</label>
                        <input type="number" name="surface_murs" class="form-control" min="0" value="80">
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label"><i class="bi bi-ground icon"></i> Surface sols/planchers (m²) :</label>
                        <input type="number" name="surface_sols" class="form-control" min="0" value="50">
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label"><i class="bi bi-fan icon"></i> Ventilation (VMC) ?</label>
                        <select name="ventilation" class="form-select">
                            <option value="non">Non</option>
                            <option value="oui">Oui</option>
                        </select>
                    </div>
                    
                    <div class="mb-4">
                        <label class="form-label"><i class="bi bi-search icon"></i> Audit logement ?</label>
                        <select name="audit" class="form-select">
                            <option value="non">Non</option>
                            <option value="oui">Oui</option>
                        </select>
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg w-100">
                        <i class="bi bi-calculator"></i> Calculer mes primes
                    </button>
                </form>
            </div>
            
            <div class="col-md-4">
                <div class="ad-banner">Pub sidebar</div>
            </div>
        </div>
        
        {% if results %}
        <div class="card mt-5 p-4">
            <h2 class="text-center mb-4">Vos gains estimés – Catégorie {{ results.categorie }}</h2>
            
            <div class="total-block">
                <div class="total-money">{{ results.total }}</div>
                <div class="total-label">Total approximatif des primes</div>
                <small style="color: #aaa;">(hors plafonds TVAC 50-70 % – cumuls possibles)</small>
            </div>
            
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="result-highlight">
                        <span class="result-label">Toiture</span>
                        <span class="money">{{ results.toiture }}</span>
                    </div>
                    <div class="result-highlight">
                        <span class="result-label">Murs</span>
                        <span class="money">{{ results.murs }}</span>
                    </div>
                    <div class="result-highlight">
                        <span class="result-label">Sols</span>
                        <span class="money">{{ results.sols }}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="result-highlight">
                        <span class="result-label">PAC air/eau</span>
                        <span class="money">{{ results.pac }}</span>
                    </div>
                    <div class="result-highlight">
                        <span class="result-label">Ventilation</span>
                        <span class="money">{{ results.ventilation }}</span>
                    </div>
                    <div class="result-highlight">
                        <span class="result-label">Audit</span>
                        <span class="money">{{ results.audit }}</span>
                    </div>
                </div>
            </div>
            
            <div class="tips-section">
                <h4 style="color: #39ff14;"><i class="bi bi-lightbulb-fill me-2"></i>Astuces & conseils</h4>
                <ul class="mb-0" style="color: #ccc;">
                    <li><strong>Biosourcé</strong> → +30 % sur isolation (laine de bois, chanvre…)</li>
                    <li><strong>Audit</strong> → prime jusqu'à 456 € (R1), souvent obligatoire</li>
                    <li><strong>Cumulez</strong> : TVA 6 %, réduction impôt 30 % toiture, prêts 0 %</li>
                    <li><strong>Autres aides</strong> : communales Hainaut, solaire, biomasse</li>
                    <li><strong>Urgence</strong> : avant 30/09/2026 pour primes directes</li>
                    <li><strong>Conseil</strong> : groupez travaux + guichet Braine-le-Comte</li>
                </ul>
            </div>
            
            <a href="https://gumroad.com/ton-produit" class="btn btn-success btn-lg w-100 mt-4" target="_blank">
                <i class="bi bi-file-earmark-pdf me-2"></i>Guide PDF + rapport détaillé (17 €)
            </a>
        </div>
        {% endif %}
        
        <div class="ad-banner mt-5">Pub bas de page</div>
        
        <p class="disclaimer">
            Disclaimer : estimations indicatives (données SPW janvier 2026). Vérifiez sur <a href="https://energie.wallonie.be" style="color: #2ecc71;">energie.wallonie.be</a>.
        </p>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    if request.method == 'POST':
        try:
            revenus_ref = float(request.form.get('revenus_ref', 0))
            cat = calcul_categorie_r(revenus_ref)
            surface_toit = float(request.form.get('surface_toit', 0))
            biosource = 'biosource' in request.form
            surface_murs = float(request.form.get('surface_murs', 0))
            surface_sols = float(request.form.get('surface_sols', 0))
            ventilation = request.form.get('ventilation', 'non') == 'oui'
            audit = request.form.get('audit', 'non') == 'oui'
            
            p_toit = prime_toiture(surface_toit, cat, biosource)
            p_murs = prime_murs(surface_murs, cat)
            p_sols = prime_sols(surface_sols, cat)
            p_pac = prime_pac(cat)
            p_vent = prime_ventilation(cat) if ventilation else 0
            p_aud = prime_audit(cat) if audit else 0
            
            total = p_toit + p_murs + p_sols + p_pac + p_vent + p_aud
            
            results = {
                'categorie': cat,
                'toiture': f"{p_toit} €",
                'murs': f"{p_murs} €",
                'sols': f"{p_sols} €",
                'pac': f"{p_pac} €",
                'ventilation': f"{p_vent} €",
                'audit': f"{p_aud} €",
                'total': f"{total} €"
            }
        except ValueError:
            results = {'error': 'Veuillez entrer des nombres valides.'}
    
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(debug=False)