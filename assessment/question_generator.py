import json
import os
from pathlib import Path


class QuestionGenerator:
    """Generates topic-wise diagnostic questions with an optional LLM backend."""

    DISTRIBUTION = ["easy", "easy", "medium", "medium", "hard"]

    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct") -> None:
        self.pipeline = None
        if os.getenv("USE_LOCAL_LLM", "").lower() in {"1", "true", "yes"}:
            try:
                from transformers import pipeline

                self.pipeline = pipeline("text-generation", model=model_name, max_new_tokens=1200)
            except Exception:
                self.pipeline = None

    def generate(self, subject: str, topic: str) -> dict:
        if topic in PROVIDED_TOPIC_QUESTION_BANK:
            return {"subject": subject, "topic": topic, "questions": PROVIDED_TOPIC_QUESTION_BANK[topic]}
        if self.pipeline:
            prompt = self._prompt(subject, topic)
            try:
                raw = self.pipeline(prompt)[0]["generated_text"]
                parsed = self._extract_json(raw)
                if parsed and len(parsed.get("questions", [])) == 5:
                    return parsed
            except Exception:
                pass
        return self._fallback(subject, topic)

    def _prompt(self, subject: str, topic: str) -> str:
        return f"""You are an expert JEE examiner.

Generate 5 high-quality JEE-style questions for the topic:
{topic}

Subject: {subject}

Requirements:
- 2 easy
- 2 medium
- 1 difficult
- Mix conceptual and numerical questions
- Follow JEE Main/Advanced style
- Include 4 options
- Include correct answer
- Include concise explanation

Return ONLY valid JSON with keys topic and questions."""

    def _extract_json(self, text: str) -> dict | None:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
        for question in payload.get("questions", []):
            if not {"question", "difficulty", "options", "correct_answer", "explanation"}.issubset(question):
                return None
        return payload

    def _fallback(self, subject: str, topic: str) -> dict:
        questions = TOPIC_QUESTION_BANK.get(topic) or self._subject_fallback(subject, topic)
        return {"subject": subject, "topic": topic, "questions": questions}

    def _subject_fallback(self, subject: str, topic: str) -> list[dict]:
        if subject == "Mathematics":
            return math_bank(topic, "f(x)=x^2+3x+2", "differentiate or simplify the expression")
        if subject == "Chemistry":
            return chemistry_bank(topic, "A + B -> C", "identify the limiting idea or concept")
        return physics_bank(topic, "s=ut+1/2 at^2", "choose the correct physical relation")


def q(text: str, difficulty: str, options: list[str], answer: str, explanation: str, qtype: str = "conceptual") -> dict:
    return {
        "question": text,
        "difficulty": difficulty,
        "type": qtype,
        "options": options,
        "correct_answer": answer,
        "explanation": explanation,
        "estimated_time_seconds": 90 if difficulty == "easy" else 150 if difficulty == "medium" else 240,
        "source": "curated_deterministic_bank",
    }


def mcq(text: str, difficulty: str, options: list[str], answer: str, explanation: str) -> dict:
    return q(text, difficulty, options, answer, explanation, "numerical" if any(char.isdigit() for char in text) else "conceptual")


PROVIDED_TOPIC_QUESTION_BANK = {
    "Units and Dimensions": [
        mcq("The dimensional formula of impulse is:", "easy", ["[MLT^-1]", "[ML^2T^-2]", "[MLT^-2]", "[ML^2T^-1]"], "A", "Impulse equals force multiplied by time, so its dimensions are MLT^-1."),
        mcq("If force F, velocity v and time t are taken as fundamental quantities, then dimensions of mass are:", "easy", ["[Fv^-1t]", "[Fvt^-1]", "[Fv^-2t]", "[Fvt]"], "A", "From F=ma and a=v/t, mass has dimensions Ft/v."),
        mcq("The percentage error in measurement of radius of a sphere is 2%. The percentage error in volume is:", "medium", ["2%", "4%", "6%", "8%"], "C", "Volume is proportional to r^3, so percentage error is 3 x 2% = 6%."),
        mcq("Which of the following quantities is dimensionless?", "medium", ["Strain", "Surface tension", "Gravitational constant", "Planck's constant"], "A", "Strain is change in length divided by original length."),
        mcq("If energy E, velocity v and force F are chosen as fundamental quantities, then dimensional formula of time is:", "hard", ["[E^0F^-1v^1]", "[EF^-1v^-1]", "[EF^-1v^-2]", "[E^0F^1v^-1]"], "B", "E/F gives length, and length/velocity gives time."),
    ],
    "Vectors": [
        mcq("The angle between vectors i + j and i - j is:", "easy", ["0°", "45°", "90°", "180°"], "C", "Their dot product is 1-1=0, so the angle is 90°."),
        mcq("The magnitude of vector 3i + 4j is:", "easy", ["3", "4", "5", "7"], "C", "Magnitude is sqrt(3^2+4^2)=5."),
        mcq("If A = 2i + 3j and B = i - 4j, then A·B equals:", "medium", ["-10", "-8", "-12", "8"], "A", "A·B = 2(1)+3(-4)=2-12=-10."),
        mcq("The resultant of two equal vectors inclined at 120° is:", "medium", ["Equal to either vector", "Zero", "Twice the vector", "Half the vector"], "A", "R=sqrt(A^2+A^2+2A^2 cos120)=A."),
        mcq("Three vectors of magnitudes 3, 4 and 5 can form:", "hard", ["Only acute triangle", "Right triangle", "Obtuse triangle", "No triangle"], "B", "3, 4, 5 satisfy Pythagoras, so they form a right triangle."),
    ],
    "Kinematics": [
        mcq("A particle moves with constant velocity. Its acceleration is:", "easy", ["Constant", "Variable", "Zero", "Infinite"], "C", "Constant velocity means no change in velocity."),
        mcq("The slope of velocity-time graph gives:", "easy", ["Velocity", "Acceleration", "Displacement", "Momentum"], "B", "Slope of a v-t graph is acceleration."),
        mcq("A body starts from rest with acceleration 2 m/s^2. Distance covered in 5 s is:", "medium", ["10 m", "20 m", "25 m", "50 m"], "C", "s=1/2 at^2=1/2 x 2 x 25=25 m."),
        mcq("A ball is thrown vertically upward with speed 20 m/s. Maximum height reached is (g = 10 m/s^2):", "medium", ["10 m", "20 m", "30 m", "40 m"], "B", "h=u^2/2g=400/20=20 m."),
        mcq("A particle covers half the distance with speed v and remaining half with speed 2v. Average speed is:", "hard", ["3v/2", "4v/3", "5v/4", "2v"], "B", "For equal distances, average speed is 2v1v2/(v1+v2)=4v/3."),
    ],
    "NLM": [
        mcq("Newton's first law defines:", "easy", ["Force", "Momentum", "Inertia", "Acceleration"], "C", "The first law is the law of inertia."),
        mcq("The SI unit of force is:", "easy", ["Joule", "Newton", "Pascal", "Watt"], "B", "Force is measured in newton."),
        mcq("A 5 kg body experiences acceleration 2 m/s^2. Force acting is:", "medium", ["2 N", "5 N", "10 N", "20 N"], "C", "F=ma=5 x 2=10 N."),
        mcq("A lift accelerates upward with acceleration a. Apparent weight of a body m is:", "medium", ["mg", "m(g - a)", "m(g + a)", "ma"], "C", "For upward acceleration, normal reaction is m(g+a)."),
        mcq("A block of mass m on rough horizontal surface is pulled by force F at angle theta. Normal reaction is:", "hard", ["mg + F sin theta", "mg - F sin theta", "mg + F cos theta", "mg - F cos theta"], "B", "The upward component F sin theta reduces the normal reaction."),
    ],
    "Work Power Energy": [
        mcq("The SI unit of work is:", "easy", ["Newton", "Joule", "Watt", "Pascal"], "B", "Work is measured in joule."),
        mcq("Kinetic energy depends on:", "easy", ["Velocity only", "Mass only", "Both mass and velocity", "None"], "C", "Kinetic energy is 1/2 mv^2."),
        mcq("A force of 10 N displaces a body by 5 m in its direction. Work done is:", "medium", ["10 J", "25 J", "50 J", "100 J"], "C", "W=Fs=10 x 5=50 J."),
        mcq("Power is defined as:", "medium", ["Force x displacement", "Work x time", "Work/time", "Energy x time"], "C", "Power is rate of doing work."),
        mcq("A body projected vertically upward loses 50% of its kinetic energy at maximum height. Height reached is:", "hard", ["u^2/2g", "u^2/4g", "u^2/8g", "3u^2/8g"], "B", "A 50% loss of initial kinetic energy equals mgh, giving h=u^2/4g."),
    ],
    "Rotation": [
        mcq("SI unit of moment of inertia is:", "easy", ["kg m", "kg m^2", "N m", "kg/m^2"], "B", "Moment of inertia has unit mass x length squared."),
        mcq("Angular momentum is conserved when:", "easy", ["Torque acts", "No external torque acts", "Force acts", "Velocity changes"], "B", "Angular momentum is conserved if net external torque is zero."),
        mcq("Moment of inertia of a ring about its diameter is:", "medium", ["MR^2", "MR^2/2", "MR^2/4", "2MR^2"], "B", "By perpendicular axis theorem, diameter MOI of ring is MR^2/2."),
        mcq("Torque is maximum when angle between force and radius vector is:", "medium", ["0°", "30°", "60°", "90°"], "D", "Torque tau=rF sin theta is maximum at 90°."),
        mcq("A solid sphere and ring roll down inclined plane. Which reaches first?", "hard", ["Ring", "Sphere", "Both together", "Depends on mass"], "B", "Solid sphere has smaller I/MR^2 than ring, so it accelerates more."),
    ],
    "Electrostatics": [
        mcq("SI unit of electric charge is:", "easy", ["Volt", "Coulomb", "Farad", "Ampere"], "B", "Charge is measured in coulomb."),
        mcq("Like charges:", "easy", ["Attract", "Repel", "Neutralize", "Rotate"], "B", "Like charges repel each other."),
        mcq("Coulomb's law force varies inversely as:", "medium", ["r", "r^2", "sqrt(r)", "r^3"], "B", "Coulomb force is proportional to 1/r^2."),
        mcq("Electric field inside a conductor is:", "medium", ["Infinite", "Constant", "Zero", "Variable"], "C", "In electrostatic equilibrium, electric field inside conductor is zero."),
        mcq("Three equal charges are placed at vertices of equilateral triangle. Net force on any one charge is:", "hard", ["kq^2/a^2", "sqrt(3) kq^2/a^2", "2kq^2/a^2", "Zero"], "B", "Two equal forces at 60° give resultant sqrt(3)F."),
    ],
    "Current Electricity": [
        mcq("SI unit of resistance is:", "easy", ["Volt", "Ampere", "Ohm", "Watt"], "C", "Resistance is measured in ohm."),
        mcq("Ohm's law is:", "easy", ["V proportional to I", "V proportional to 1/I", "R proportional to I", "P proportional to V"], "A", "Ohm's law states V=IR, so V is proportional to I for constant R."),
        mcq("Equivalent resistance of two 6 ohm resistors in parallel is:", "medium", ["12 ohm", "6 ohm", "3 ohm", "1.5 ohm"], "C", "Two equal resistors R in parallel give R/2=3 ohm."),
        mcq("Current through 10 ohm resistor connected to 20 V battery is:", "medium", ["0.5 A", "1 A", "2 A", "4 A"], "C", "I=V/R=20/10=2 A."),
        mcq("A wire is stretched to double its length. Its resistance becomes:", "hard", ["R/2", "R", "2R", "4R"], "D", "With volume constant, length doubles and area halves, so resistance becomes 4R."),
    ],
    "Mole Concept": [
        mcq("One mole of oxygen molecules contains:", "easy", ["6.022 x 10^23 atoms", "3.011 x 10^23 molecules", "6.022 x 10^23 molecules", "1 mole atoms"], "C", "One mole of molecules contains Avogadro number of molecules."),
        mcq("Molar mass of H2SO4 is:", "easy", ["96 g/mol", "98 g/mol", "100 g/mol", "102 g/mol"], "B", "2(1)+32+4(16)=98 g/mol."),
        mcq("Number of moles in 44 g CO2 is:", "medium", ["0.5", "1", "2", "22"], "B", "Molar mass of CO2 is 44 g/mol, so moles=1."),
        mcq("At STP, 22.4 L of gas contains:", "medium", ["1 molecule", "1 mole", "6.022 x 10^22 molecules", "2 moles"], "B", "One mole of ideal gas occupies 22.4 L at STP."),
        mcq("Empirical formula of compound containing 40% C, 6.67% H and 53.33% O is:", "hard", ["CH2O", "C2H4O2", "CHO", "C2H2O"], "A", "Mole ratio C:H:O is approximately 1:2:1."),
    ],
    "Chemical Bonding": [
        mcq("Bond formed by sharing electrons is:", "easy", ["Ionic", "Covalent", "Metallic", "Hydrogen"], "B", "Covalent bonds form by sharing electrons."),
        mcq("Shape of methane is:", "easy", ["Linear", "Bent", "Tetrahedral", "Trigonal planar"], "C", "Methane is sp3 hybridised and tetrahedral."),
        mcq("Hybridization of carbon in ethene is:", "medium", ["sp", "sp2", "sp3", "dsp2"], "B", "Each carbon in ethene is sp2 hybridised."),
        mcq("Which molecule is polar?", "medium", ["CO2", "CH4", "NH3", "BF3"], "C", "NH3 has trigonal pyramidal geometry and net dipole."),
        mcq("Bond order of O2+ is:", "hard", ["1", "1.5", "2", "2.5"], "D", "Removing one electron from antibonding orbital increases O2 bond order from 2 to 2.5."),
    ],
    "Thermodynamics": [
        mcq("First law of thermodynamics is based on conservation of:", "easy", ["Mass", "Energy", "Momentum", "Charge"], "B", "The first law expresses conservation of energy."),
        mcq("SI unit of entropy is:", "easy", ["J", "J/mol", "J mol^-1 K^-1", "KJ"], "C", "Molar entropy is commonly expressed in J mol^-1 K^-1."),
        mcq("For an isothermal process of ideal gas:", "medium", ["Delta U = 0", "Delta U > 0", "Delta U < 0", "Delta H = 0 always"], "A", "Internal energy of ideal gas depends only on temperature."),
        mcq("Enthalpy change at constant pressure equals:", "medium", ["Heat exchanged", "Work done", "Internal energy", "Entropy"], "A", "At constant pressure, heat exchanged equals enthalpy change."),
        mcq("Efficiency of Carnot engine operating between 500 K and 300 K is:", "hard", ["20%", "30%", "40%", "60%"], "C", "Efficiency = 1 - Tc/Th = 1 - 300/500 = 40%."),
    ],
    "Equilibrium": [
        mcq("pH of neutral solution at 25°C is:", "easy", ["0", "7", "14", "1"], "B", "Neutral water has pH 7 at 25°C."),
        mcq("Catalyst affects:", "easy", ["Equilibrium constant", "Rate only", "Delta G", "Enthalpy"], "B", "Catalyst changes rate, not equilibrium constant."),
        mcq("For equilibrium N2 + 3H2 <=> 2NH3, increase in pressure shifts equilibrium:", "medium", ["Left", "Right", "No change", "Randomly"], "B", "Higher pressure favours side with fewer gas moles."),
        mcq("Value of ionic product of water at 25°C is:", "medium", ["10^-7", "10^-14", "10^7", "1"], "B", "Kw at 25°C is 10^-14."),
        mcq("For weak acid HA, degree of dissociation increases on:", "hard", ["Increasing concentration", "Decreasing temperature", "Dilution", "Adding common ion"], "C", "Dilution increases degree of dissociation of weak electrolyte."),
    ],
    "Organic Chemistry": [
        mcq("General formula of alkane is:", "easy", ["CnH2n", "CnH2n+2", "CnH2n-2", "CnH2n+1"], "B", "Alkanes follow CnH2n+2."),
        mcq("Functional group of alcohol is:", "easy", ["-CHO", "-COOH", "-OH", "-O-"], "C", "Alcohols contain hydroxyl group."),
        mcq("IUPAC name of CH3CH2CHO is:", "medium", ["Propanal", "Propanone", "Ethanal", "Propanol"], "A", "Three-carbon aldehyde is propanal."),
        mcq("Which reaction gives alkene from alcohol?", "medium", ["Hydration", "Oxidation", "Dehydration", "Reduction"], "C", "Alcohols form alkenes by dehydration."),
        mcq("Number of structural isomers of C5H12 is:", "hard", ["2", "3", "4", "5"], "B", "Pentane has n-pentane, isopentane, and neopentane."),
    ],
    "Coordination Compounds": [
        mcq("Central metal ion in [Cu(NH3)4]^2+ is:", "easy", ["NH3", "Cu", "Cu^2+", "N"], "C", "The complex has copper in +2 oxidation state."),
        mcq("Coordination number of Co in [Co(NH3)6]^3+ is:", "easy", ["3", "4", "5", "6"], "D", "Six NH3 ligands coordinate to cobalt."),
        mcq("Ligands donating two lone pairs are called:", "medium", ["Monodentate", "Ambidentate", "Bidentate", "Neutral"], "C", "Bidentate ligands donate through two donor atoms."),
        mcq("IUPAC name of K4[Fe(CN)6] is:", "medium", ["Potassium hexacyanoferrate(II)", "Potassium cyanide iron", "Potassium ferrocyanide", "Potassium ferricyanide"], "A", "The anion is hexacyanoferrate(II)."),
        mcq("Hybridization of [Ni(CN)4]^2- is:", "hard", ["sp3", "dsp2", "d2sp3", "sp2"], "B", "Strong-field CN- gives square planar dsp2 complex."),
    ],
    "Limits": [
        mcq("lim x->0 (sin x)/x equals:", "easy", ["0", "1", "infinity", "-1"], "B", "This is a standard limit equal to 1."),
        mcq("lim x->infinity 1/x equals:", "easy", ["1", "infinity", "0", "-infinity"], "C", "1/x tends to zero as x grows without bound."),
        mcq("lim x->0 (1 - cos x)/x^2 equals:", "medium", ["1", "1/2", "0", "2"], "B", "Using expansion, 1-cos x is approximately x^2/2."),
        mcq("lim x->a (x^2 - a^2)/(x - a) equals:", "medium", ["a", "2a", "a^2", "0"], "B", "Factor numerator as (x-a)(x+a), then substitute x=a."),
        mcq("lim x->0 [(e^x - 1 - x)/x^2] equals:", "hard", ["0", "1/2", "1", "2"], "B", "Expansion e^x=1+x+x^2/2+... gives limit 1/2."),
    ],
    "Differentiation": [
        mcq("Derivative of x^2 is:", "easy", ["x", "2x", "x^2", "2"], "B", "By power rule, d(x^2)/dx=2x."),
        mcq("Derivative of sin x is:", "easy", ["cos x", "-sin x", "tan x", "sec^2 x"], "A", "d(sin x)/dx=cos x."),
        mcq("Derivative of ln x is:", "medium", ["x", "1/x", "e^x", "ln x"], "B", "d(ln x)/dx=1/x."),
        mcq("If y = x^3 + 2x, then dy/dx at x = 1 is:", "medium", ["3", "4", "5", "6"], "C", "dy/dx=3x^2+2, so at x=1 it is 5."),
        mcq("If y = (sin x)^x, then log differentiation involves:", "hard", ["Product rule only", "Chain rule only", "Logarithmic differentiation", "Partial differentiation"], "C", "Variable base and exponent are handled using logarithmic differentiation."),
    ],
    "AOD": [
        mcq("At maxima, derivative changes from:", "easy", ["Positive to negative", "Negative to positive", "Zero to positive", "Positive to zero"], "A", "At a local maximum, derivative changes from + to -."),
        mcq("Slope of tangent to curve at a point is:", "easy", ["y/x", "dy/dx", "dx/dy", "xy"], "B", "Derivative gives slope of tangent."),
        mcq("Function increasing in interval if:", "medium", ["dy/dx < 0", "dy/dx > 0", "dy/dx = 0", "dy/dx undefined"], "B", "Positive derivative indicates increasing function."),
        mcq("Minimum value of x^2 + 1 is:", "medium", ["0", "1", "2", "-1"], "B", "x^2 is minimum 0, so x^2+1 is minimum 1."),
        mcq("Equation of tangent to y = x^2 at x = 1 is:", "hard", ["y = x", "y = 2x - 1", "y = x + 1", "y = 2x + 1"], "B", "At x=1, y=1 and slope=2, so y-1=2(x-1)."),
    ],
    "Integration": [
        mcq("Integral of dx equals:", "easy", ["x", "x + C", "1", "0"], "B", "Indefinite integral includes constant of integration."),
        mcq("Integral of x dx equals:", "easy", ["x^2", "x^2/2 + C", "2x", "ln x"], "B", "Using power rule, integral x dx=x^2/2+C."),
        mcq("Integral of cos x dx equals:", "medium", ["sin x + C", "-sin x + C", "tan x + C", "sec x + C"], "A", "Derivative of sin x is cos x."),
        mcq("Integral of 1/x dx equals:", "medium", ["x", "ln|x| + C", "1/x", "e^x"], "B", "Integral of 1/x is ln|x|+C."),
        mcq("Integral of e^x sin x dx requires:", "hard", ["Substitution", "Partial fractions", "Integration by parts twice", "Trigonometric substitution"], "C", "This standard integral is solved by applying integration by parts twice."),
    ],
    "Differential Equations": [
        mcq("Order of equation d^2y/dx^2 + dy/dx + y = 0 is:", "easy", ["1", "2", "3", "0"], "B", "The highest derivative is second order."),
        mcq("Degree of (dy/dx)^2 + y = 0 is:", "easy", ["1", "2", "3", "Undefined"], "B", "The equation is polynomial in derivative and highest derivative has power 2."),
        mcq("General solution of dy/dx = 0 is:", "medium", ["y = x", "y = C", "y = e^x", "y = x^2"], "B", "Zero derivative implies y is constant."),
        mcq("Variable separable equation is:", "medium", ["dy/dx = x + y", "dy/dx = xy", "dy/dx = x/y", "dy/dx = y - x"], "C", "dy/dx=x/y gives y dy = x dx, separable."),
        mcq("Integrating factor method is mainly used for:", "hard", ["Exact equations", "Linear differential equations", "Homogeneous equations", "Bernoulli theorem"], "B", "Integrating factors are central to first-order linear differential equations."),
    ],
    "Matrices": [
        mcq("A matrix with equal rows and columns is:", "easy", ["Rectangular", "Square", "Null", "Diagonal"], "B", "Equal number of rows and columns defines a square matrix."),
        mcq("Determinant of identity matrix is:", "easy", ["0", "1", "-1", "Depends on order"], "B", "The determinant of identity matrix is 1."),
        mcq("If A is 2x3 and B is 3x2, then AB is of order:", "medium", ["2x2", "3x3", "2x3", "3x2"], "A", "Outer dimensions determine product order: 2x2."),
        mcq("Inverse of matrix exists only if determinant is:", "medium", ["Zero", "Positive", "Negative", "Non-zero"], "D", "A matrix is invertible iff determinant is non-zero."),
        mcq("If A is skew-symmetric, then diagonal elements are:", "hard", ["1", "Equal", "Zero", "Undefined"], "C", "For skew-symmetric matrix, a_ii=-a_ii, so diagonal entries are zero."),
    ],
    "Probability": [
        mcq("Probability of sure event is:", "easy", ["0", "1", "1/2", "Infinite"], "B", "A sure event has probability 1."),
        mcq("Probability of impossible event is:", "easy", ["0", "1", "-1", "1/2"], "A", "An impossible event has probability 0."),
        mcq("A coin is tossed once. Probability of getting head is:", "medium", ["0", "1", "1/2", "1/4"], "C", "There is one favourable outcome out of two equally likely outcomes."),
        mcq("A die is thrown. Probability of getting even number is:", "medium", ["1/6", "1/3", "1/2", "2/3"], "C", "Even outcomes are 2, 4, 6, so probability is 3/6=1/2."),
        mcq("Two cards are drawn from deck without replacement. Probability both are aces is:", "hard", ["1/13", "1/221", "4/52", "1/52"], "B", "Probability is (4/52)(3/51)=1/221."),
    ],
}


def physics_bank(topic: str, formula: str, hard_prompt: str) -> list[dict]:
    numerical = PHYSICS_NUMERICALS.get(topic, ("a measured value changes from 2 to 10 in 4 s. Find the rate of change.", ["1", "2", "3", "8"], "B", "Rate of change = (10-2)/4 = 2."))
    return [
        q(f"In {topic}, which relation is normally used as a core starting point?", "easy", [formula, "E=mc^2", "PV=nRT", "n lambda = 2d sin theta"], "A", f"{formula} is a standard relation used in {topic}."),
        q(f"In a {topic} problem, which setup step is most important before calculation?", "easy", ["Draw the physical diagram and mark directions/signs", "Guess from options", "Ignore units", "Use the longest formula"], "A", "JEE physics rewards a correct model before substitution."),
        q(f"For {topic}, {numerical[0]}", "medium", numerical[1], numerical[2], numerical[3], "numerical"),
        q(f"Which error most commonly breaks multi-step {topic} problems?", "medium", ["Keeping units consistent", "Mixing scalar and vector directions", "Checking limiting cases", "Drawing free-body or motion diagrams"], "B", "Direction or sign mistakes are a major source of wrong physics answers."),
        q(f"In an advanced {topic} problem, {hard_prompt}. Which strategy is strongest?", "hard", ["Apply one memorized formula", "Split into constraints, conservation laws, and target variable", "Avoid diagrams", "Use option elimination only"], "B", "Advanced physics problems usually combine constraints with a governing principle.", "application"),
    ]


def chemistry_bank(topic: str, equation: str, hard_prompt: str) -> list[dict]:
    numerical = CHEMISTRY_NUMERICALS.get(topic, ("a reaction has theoretical yield 10 mol and actual yield 7 mol. Find percentage yield.", ["30%", "70%", "100%", "143%"], "B", "Percentage yield = actual/theoretical x 100 = 70%."))
    return [
        q(f"For {topic}, what is the most reliable first check in the equation {equation}?", "easy", ["Balanced atoms and charge", "Alphabetical order", "Colour of paper", "Length of equation"], "A", "Stoichiometry and charge balance are foundational checks in chemistry."),
        q(f"In {topic}, which evidence best indicates a concept has been understood?", "easy", ["Only memorising the final answer", "Explaining the trend or mechanism", "Skipping exceptions", "Solving without units"], "B", "JEE chemistry often tests why a trend, structure, or reaction behaves a certain way."),
        q(f"For {topic}, {numerical[0]}", "medium", numerical[1], numerical[2], numerical[3], "numerical"),
        q(f"Which practice is best for medium-level {topic} questions?", "medium", ["Memorise isolated facts", "Link formula, condition, exception, and example", "Avoid mechanisms", "Attempt only easy questions"], "B", "Medium JEE chemistry questions usually combine facts with conditions or reasoning."),
        q(f"In an advanced {topic} problem, {hard_prompt}. What should be prioritized?", "hard", ["Identify governing concept and exceptions", "Pick the most familiar option", "Ignore the given condition", "Use unrelated reactions"], "A", "Hard chemistry questions often hinge on conditions, exceptions, and mechanism-level reasoning.", "application"),
    ]


def math_bank(topic: str, expression: str, hard_prompt: str) -> list[dict]:
    numerical = MATH_NUMERICALS.get(topic, (f"if {expression}, what is f(1)?", ["4", "5", "6", "7"], "C", "Substitute x=1: 1+3+2=6."))
    medium = MATH_MEDIUMS.get(topic, ("solve x^2-5x+6=0.", ["1, 6", "2, 3", "-2, -3", "0, 6"], "B", "Factorize as (x-2)(x-3)=0."))
    concept = MATH_CONCEPTS.get(topic, ("if a derivative changes sign from positive to negative at x=a, what is indicated?", ["Local maximum", "No extremum ever", "Always minimum", "Function is discontinuous"], "A", "A positive-to-negative derivative sign change indicates a local maximum."))
    return [
        q(f"For {topic}, {numerical[0]}", "easy", numerical[1], numerical[2], numerical[3], "numerical"),
        q(f"In {topic}, which habit reduces calculation errors?", "easy", ["Skip domain checks", "Write domain and transformation steps", "Use only mental math", "Avoid simplification"], "B", "Domain and clean algebra steps prevent common JEE mistakes."),
        q(f"For {topic}, {medium[0]}", "medium", medium[1], medium[2], medium[3], "numerical"),
        q(f"In {topic}, {concept[0]}", "medium", concept[1], concept[2], concept[3]),
        q(f"In a hard {topic} question, {hard_prompt}. What is the most reliable approach?", "hard", ["Start with random substitution", "Break the expression into known identities and constraints", "Ignore domain", "Differentiate every expression blindly"], "B", "Hard maths problems become tractable when decomposed into identities, constraints, and target form.", "application"),
    ]


PHYSICS_NUMERICALS = {
    "Units and Dimensions": ("force has dimensions M L T^-2. What are dimensions of impulse?", ["M L T^-1", "M L T^-2", "M L^2 T^-2", "M T^-1"], "A", "Impulse = force x time, so dimensions are M L T^-1."),
    "Vectors": ("A=3i+4j. What is |A|?", ["3", "4", "5", "7"], "C", "|A| = sqrt(3^2+4^2)=5."),
    "Kinematics": ("a body starts from rest with acceleration 2 m/s^2 for 3 s. Find displacement.", ["6 m", "9 m", "12 m", "18 m"], "B", "s=1/2 at^2 = 1/2 x 2 x 9 = 9 m."),
    "NLM": ("a 2 kg block accelerates at 3 m/s^2. Find net force.", ["2 N", "3 N", "5 N", "6 N"], "D", "F=ma=2 x 3=6 N."),
    "Work Power Energy": ("a 4 N force moves a body 3 m in its direction. Find work.", ["7 J", "12 J", "1.33 J", "0 J"], "B", "W=Fs cos0 = 4 x 3 = 12 J."),
    "Rotation": ("angular velocity changes from 2 rad/s to 10 rad/s in 4 s. Find angular acceleration.", ["1 rad/s^2", "2 rad/s^2", "3 rad/s^2", "8 rad/s^2"], "B", "alpha=(omega-u)/t=(10-2)/4=2 rad/s^2."),
    "Electrostatics": ("two equal charges are separated by r. If distance is doubled, force becomes", ["F/2", "F/4", "2F", "4F"], "B", "Coulomb force varies as 1/r^2."),
    "Current Electricity": ("a 6 ohm resistor carries 2 A current. Find voltage.", ["3 V", "6 V", "8 V", "12 V"], "D", "V=IR=2 x 6=12 V."),
    "Modern Physics": ("a photon has frequency f. If frequency doubles, energy becomes", ["E/2", "E", "2E", "4E"], "C", "E=hf, so energy is proportional to frequency."),
}


CHEMISTRY_NUMERICALS = {
    "Mole Concept": ("how many moles are present in 18 g of H2O? Molar mass=18 g/mol.", ["0.5", "1", "2", "18"], "B", "Moles = mass/molar mass = 18/18 = 1."),
    "Chemical Bonding": ("in NH3, what is the hybridisation of nitrogen?", ["sp", "sp2", "sp3", "dsp2"], "C", "Nitrogen has three bond pairs and one lone pair, giving sp3 hybridisation."),
    "Thermodynamics": ("if Delta H=40 kJ and T Delta S=10 kJ, find Delta G.", ["30 kJ", "50 kJ", "-30 kJ", "-50 kJ"], "A", "Delta G = Delta H - T Delta S = 40 - 10 = 30 kJ."),
    "Equilibrium": ("for N2 + 3H2 <=> 2NH3, increasing pressure shifts equilibrium toward", ["reactants", "products", "no change", "only catalyst side"], "B", "Products have fewer gas moles, so high pressure favours NH3."),
    "Organic Chemistry": ("CH3Br + OH- -> CH3OH + Br- is best classified as", ["addition", "elimination", "nucleophilic substitution", "free radical halogenation"], "C", "OH- replaces Br-, so it is nucleophilic substitution."),
    "Coordination Compounds": ("in [Co(NH3)6]Cl3, oxidation state of Co is", ["0", "+2", "+3", "+6"], "C", "NH3 is neutral and three chloride ions balance a +3 complex ion."),
}


MATH_NUMERICALS = {
    "Functions": ("if f(x)=x^2+3x+2, what is f(1)?", ["4", "5", "6", "7"], "C", "f(1)=1+3+2=6."),
    "Limits": ("evaluate lim x->1 (x^2-1)/(x-1).", ["0", "1", "2", "Does not exist"], "C", "Factor x^2-1=(x-1)(x+1), limit is 2."),
    "Differentiation": ("if f(x)=x^3+2x, find f'(1).", ["3", "4", "5", "6"], "C", "f'(x)=3x^2+2, so f'(1)=5."),
    "AOD": ("for f(x)=x^3-3x, find f'(x).", ["3x^2-3", "x^2-3", "3x-3", "x^3-3"], "A", "Differentiate term-wise: 3x^2-3."),
    "Integration": ("evaluate integral of 2x dx.", ["x+C", "x^2+C", "2+C", "2x^2+C"], "B", "Integral of 2x is x^2+C."),
    "Differential Equations": ("solve dy/dx=2x in simplest integrated form.", ["y=x+C", "y=x^2+C", "y=2x+C", "y=2x^2+C"], "B", "Integrating both sides gives y=x^2+C."),
    "Matrices": ("determinant of [[1,2],[3,4]] is", ["-2", "2", "10", "-10"], "A", "ad-bc=1*4-2*3=-2."),
    "Probability": ("a fair die is thrown once. Probability of an even number is", ["1/6", "1/3", "1/2", "2/3"], "C", "Even outcomes are 2,4,6 out of 6, so probability is 3/6=1/2."),
}


MATH_MEDIUMS = {
    "Functions": ("if f(x)=2x+1 and g(x)=x^2, find f(g(2)).", ["5", "7", "9", "16"], "C", "g(2)=4 and f(4)=9."),
    "Limits": ("evaluate lim x->0 sin(3x)/x.", ["0", "1", "3", "Does not exist"], "C", "sin(3x)/(3x) -> 1, so the limit is 3."),
    "Differentiation": ("differentiate sin x + x^2.", ["cos x + 2x", "-cos x + 2x", "sin x + 2", "cos x + x"], "A", "Derivative of sin x is cos x and derivative of x^2 is 2x."),
    "AOD": ("for f(x)=x^2-4x+3, the critical point is x=", ["0", "1", "2", "4"], "C", "f'(x)=2x-4=0 gives x=2."),
    "Integration": ("evaluate integral from 0 to 1 of 2x dx.", ["0", "1", "2", "4"], "B", "Integral is x^2 from 0 to 1, equal to 1."),
    "Differential Equations": ("solve dy/dx = y for the general form.", ["y=Cx", "y=Ce^x", "y=C/x", "y=x+C"], "B", "dy/y=dx integrates to ln y=x+C, so y=Ce^x."),
    "Matrices": ("for A=[[1,0],[0,1]], A^2 equals", ["0 matrix", "A", "2A", "-A"], "B", "The identity matrix squared is itself."),
    "Probability": ("two coins are tossed. Probability of exactly one head is", ["1/4", "1/2", "3/4", "1"], "B", "Outcomes HT and TH are 2 out of 4."),
}


MATH_CONCEPTS = {
    "Functions": ("what does one-one function mean?", ["Every input has two outputs", "Distinct inputs have distinct outputs", "All outputs are zero", "Domain equals integers only"], "B", "One-one means no two distinct inputs map to the same output."),
    "Limits": ("which condition supports direct substitution?", ["Function is continuous at the point", "Denominator is zero only", "Expression is longest", "Variable is absent"], "A", "Continuity allows direct substitution."),
    "Differentiation": ("what does derivative represent geometrically?", ["Area under curve", "Slope of tangent", "Length of curve", "Y-intercept only"], "B", "Derivative gives instantaneous slope."),
    "AOD": ("if f'(x)>0 on an interval, the function is", ["Decreasing", "Constant", "Increasing", "Discontinuous"], "C", "Positive derivative implies increasing behaviour."),
    "Integration": ("what does a definite integral often represent geometrically?", ["Slope only", "Area with sign", "Root count", "Domain only"], "B", "A definite integral gives signed area under the curve."),
    "Differential Equations": ("what is order of a differential equation?", ["Highest power", "Highest derivative present", "Number of constants only", "Degree of x"], "B", "Order is determined by the highest derivative."),
    "Matrices": ("a square matrix is invertible when", ["determinant is zero", "determinant is non-zero", "all entries are positive", "trace is zero"], "B", "A matrix is invertible iff its determinant is non-zero."),
    "Probability": ("for independent events A and B, P(A intersection B) equals", ["P(A)+P(B)", "P(A)P(B)", "P(A)-P(B)", "1"], "B", "Independent event intersection probability is product."),
}


TOPIC_QUESTION_BANK = {
    "Units and Dimensions": physics_bank("Units and Dimensions", "v=u+at", "two candidate formulas look similar but only one is dimensionally valid"),
    "Vectors": physics_bank("Vectors", "|A+B|^2=A^2+B^2+2AB cos theta", "components in two perpendicular directions must be combined"),
    "Kinematics": physics_bank("Kinematics", "s=ut+1/2 at^2", "a motion graph and two time intervals are both given"),
    "NLM": physics_bank("NLM", "F=ma", "multiple blocks are connected and friction is present"),
    "Work Power Energy": physics_bank("Work Power Energy", "W=Delta K", "a body moves on a rough curved track"),
    "Rotation": physics_bank("Rotation", "tau=I alpha", "rolling motion combines translation and rotation"),
    "Electrostatics": physics_bank("Electrostatics", "F=kq1q2/r^2", "fields from multiple charges must be superposed"),
    "Current Electricity": physics_bank("Current Electricity", "V=IR", "a bridge circuit contains series and parallel reductions"),
    "Modern Physics": physics_bank("Modern Physics", "E=hf", "photoelectric threshold and stopping potential are both involved"),
    "Mole Concept": chemistry_bank("Mole Concept", "2H2 + O2 -> 2H2O", "limiting reagent and leftover reagent must both be found"),
    "Chemical Bonding": chemistry_bank("Chemical Bonding", "Na+ + Cl- -> NaCl", "hybridisation, shape, and polarity are all being tested"),
    "Thermodynamics": chemistry_bank("Thermodynamics", "Delta G = Delta H - T Delta S", "spontaneity changes with temperature"),
    "Equilibrium": chemistry_bank("Equilibrium", "N2 + 3H2 <=> 2NH3", "Le Chatelier shift and Kp/Kc relation are both involved"),
    "Organic Chemistry": chemistry_bank("Organic Chemistry", "CH3Br + OH- -> CH3OH + Br-", "mechanism, nucleophile strength, and solvent effect interact"),
    "Coordination Compounds": chemistry_bank("Coordination Compounds", "[Co(NH3)6]Cl3", "oxidation state, coordination number, and isomerism are tested"),
    "Functions": math_bank("Functions", "f(x)=x^2+3x+2", "domain and composition are both involved"),
    "Limits": math_bank("Limits", "f(x)=(x^2-1)/(x-1)", "direct substitution gives an indeterminate form"),
    "Differentiation": math_bank("Differentiation", "f(x)=x^3+2x", "chain rule and product rule appear together"),
    "AOD": math_bank("AOD", "f(x)=x^3-3x", "monotonicity and extrema must be identified"),
    "Integration": math_bank("Integration", "f(x)=2x+3", "substitution and definite integral properties are both useful"),
    "Differential Equations": math_bank("Differential Equations", "dy/dx=2x", "variables must be separated before integrating"),
    "Matrices": math_bank("Matrices", "f(x)=x^2+3x+2", "determinant conditions decide invertibility"),
    "Probability": math_bank("Probability", "f(x)=x^2+3x+2", "conditional probability must be separated from independent probability"),
}


def save_question_set(question_set: dict, output_dir: str | Path = "data/generated_tests") -> Path:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    topic_slug = question_set["topic"].lower().replace(" ", "_")
    path = Path(output_dir) / f"{topic_slug}.json"
    path.write_text(json.dumps(question_set, indent=2), encoding="utf-8")
    return path
