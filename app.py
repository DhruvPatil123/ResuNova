import streamlit as st
from streamlit_components_v1 import html
from data.schema import ResumeData, Experience, Education
from core.ai_engine import AIEngine
from core.ats_scorer import ATSScorer
from core.pdf_generator import PDFGenerator
from core.parser import ResumeParser
import io

# Page Configuration
st.set_page_config(
    page_title="ResuNova | AI 3D Resume Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Advanced CSS for 3D Transitions & Theming ---
st.markdown("""
    <style>
    .stApp { background: transparent; }
    #background-canvas {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
    }
    div[data-testid="stSidebar"] {
        background-color: rgba(20, 20, 35, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease;
    }
    .main-card:hover { transform: translateZ(10px); }
    </style>
    """, unsafe_allow_html=True)

def render_3d_background():
    three_js_code = """
    <div id="background-canvas"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        (function() {
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('background-canvas').appendChild(renderer.domElement);
            const geometry = new THREE.BufferGeometry();
            const vertices = [];
            for (let i = 0; i < 5000; i++) {
                vertices.push(THREE.MathUtils.randFloatSpread(2000), THREE.MathUtils.randFloatSpread(2000), THREE.MathUtils.randFloatSpread(2000));
            }
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            const particles = new THREE.Points(geometry, new THREE.PointsMaterial({ color: 0x6a5acd, size: 2 }));
            scene.add(particles);
            camera.position.z = 1000;
            function animate() {
                requestAnimationFrame(animate);
                particles.rotation.x += 0.0005;
                particles.rotation.y += 0.0005;
                renderer.render(scene, camera);
            }
            animate();
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        })();
    </script>
    """
    html(three_js_code, height=0)

# State Initialization
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = ResumeData()
if 'ats_results' not in st.session_state:
    st.session_state.ats_results = None
if 'token_usage' not in st.session_state:
    st.session_state.token_usage = 0

def main():
    render_3d_background()
    ai = AIEngine()
    scorer = ATSScorer()
    parser = ResumeParser()

    st.title("🚀 ResuNova")
    st.subheader("Build a resume that passes machines and impresses humans.")

    menu = ["Dashboard", "Profile", "Experience", "Skills & Education", "ATS Tuner", "Export", "Admin"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Dashboard":
        st.markdown("### 🌟 Command Center")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="main-card">
                <h4 style="color: white;">Welcome to the Future of Resumes</h4>
                <p style="color: #ccc;">Your career is an evolution. Your resume should be too.</p>
                <p style="color: #aaa; font-size: 14px;">Fill in your details, use AI to quantify your impact, and get a perfect ATS score.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 📂 Quick Import")
            uploaded_file = st.file_uploader("Upload existing Resume (PDF)", type="pdf")
            if uploaded_file:
                with st.spinner("Parsing PDF..."):
                    parsed = parser.parse_pdf(uploaded_file)
                    st.session_state.resume_data.full_name = parsed['full_name']
                    st.session_state.resume_data.summary = parsed['summary']
                    st.success("Basic info imported! Check Profile tab.")

    elif choice == "Profile":
        st.markdown("### 👤 Personal Information")
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.resume_data.full_name = st.text_input("Full Name", st.session_state.resume_data.full_name)
                st.session_state.resume_data.email = st.text_input("Email", st.session_state.resume_data.email)
                st.session_state.resume_data.phone = st.text_input("Phone", st.session_state.resume_data.phone)
            with col2:
                st.session_state.resume_data.linkedin = st.text_input("LinkedIn URL", st.session_state.resume_data.linkedin)
                st.session_state.resume_data.github = st.text_input("GitHub URL", st.session_state.resume_data.github)
                st.session_state.resume_data.portfolio = st.text_input("Portfolio URL", st.session_state.resume_data.portfolio)

            st.session_state.resume_data.summary = st.text_area("Professional Summary", st.session_state.resume_data.summary)
            submit = st.form_submit_button("Save Profile")
            if submit:
                st.success("Profile Updated!")

    elif choice == "Experience":
        st.markdown("### 💼 Experience & Impact Hub")
        if not hasattr(st.session_state.resume_data, 'experience') or st.session_state.resume_data.experience is None:
            st.session_state.resume_data.experience = []

        if st.button("➕ Add Work Experience"):
            st.session_state.resume_data.experience.append(Experience())
            st.rerun()

        for idx, exp in enumerate(st.session_state.resume_data.experience):
            with st.expander(f"Experience #{idx+1}: {exp.company or 'New Company'}"):
                col1, col2 = st.columns(2)
                with col1:
                    exp.company = st.text_input(f"Company", exp.company, key=f"comp_{idx}")
                    exp.role = st.text_input(f"Role", exp.role, key=f"role_{idx}")
                with col2:
                    exp.start_date = st.text_input(f"Start Date", exp.start_date, key=f"start_{idx}")
                    exp.end_date = st.text_input(f"End Date", exp.end_date, key=f"end_{idx}")

                st.markdown("**Achievements**")
                for b_idx, bullet in enumerate(exp.description):
                    b_col1, b_col2 = st.columns([4, 1])
                    with b_col1:
                        new_bullet = st.text_input(f"Bullet {b_idx+1}", bullet, key=f"bullet_{idx}_{b_idx}")
                        exp.description[b_idx] = new_bullet
                    with b_col2:
                        if st.button(f"✨ AI", key=f"ai_{idx}_{b_idx}"):
                            improved = ai.quantify_bullet(bullet)
                            if "⚠️" in improved: st.error(improved)
                            else:
                                exp.description[b_idx] = improved
                                st.rerun()
                if st.button("➕ Add Bullet", key=f"add_b_{idx}"):
                    exp.description.append("")
                    st.rerun()
                if st.button(f"🗑️ Remove", key=f"rem_{idx}"):
                    st.session_state.resume_data.experience.pop(idx)
                    st.rerun()

    elif choice == "Skills & Education":
        st.markdown("### 🎓 Skills & Education")
        st.markdown("#### Education")
        if st.button("➕ Add Education"):
            st.session_state.resume_data.education.append(Education())
            st.rerun()
        for idx, edu in enumerate(st.session_state.resume_data.education):
            with st.expander(f"Education #{idx+1}"):
                col1, col2 = st.columns(2)
                with col1: edu.institution = st.text_input("Institution", edu.institution, key=f"edu_i_{idx}")
                with col2: edu.degree = st.text_input("Degree", edu.degree, key=f"edu_d_{idx}")
                if st.button(f"🗑️ Remove", key=f"rem_edu_{idx}"):
                    st.session_state.resume_data.education.pop(idx)
                    st.rerun()
        st.markdown("---")
        st.markdown("#### Technical Skills")
        skills_input = st.text_area("Skills (comma separated)", value=", ".join(st.session_state.resume_data.skills))
        st.session_state.resume_data.skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    elif choice == "ATS Tuner":
        st.markdown("### 🎯 ATS Tuning Room")
        col_input, col_visual = st.columns([1, 1])
        with col_input:
            job_desc = st.text_area("Job Description", height=300)
            if st.button("Analyze Resume 🚀"):
                st.session_state.ats_results = scorer.analyze(st.session_state.resume_data, job_desc)

            if st.button("🪄 Auto-Tailor Whole Resume"):
                with st.spinner("AI is rewriting for the JD..."):
                    new_exp_data = ai.rewrite_experience_for_jd(st.session_state.resume_data.experience, job_desc)
                    if isinstance(new_exp_data, list):
                        for i, item in enumerate(new_exp_data):
                            if i < len(st.session_state.resume_data.experience):
                                st.session_state.resume_data.experience[i].description = item['description']
                    st.success("Resume tailored! Check the Experience tab.")

        with col_visual:
            if st.session_state.ats_results:
                res = st.session_state.ats_results
                score = res['score']
                gauge_html = f"""
                <div style="display: flex; justify-content: center; align-items: center; height: 300px;">
                    <div id="gauge-container"></div>
                </div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <script>
                    (function() {{
                        const scene = new THREE.Scene();
                        const camera = new THREE.PerspectiveCamera(75, 300/300, 0.1, 1000);
                        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                        renderer.setSize(300, 300);
                        document.getElementById('gauge-container').appendChild(renderer.domElement);
                        const geometry = new THREE.TorusGeometry(10, 3, 16, 100);
                        const material = new THREE.MeshStandardMaterial({{
                            color: { "0x00ff00" if score > 80 else "0xffee00" if score > 50 else "0xff0000" },
                            emissive: { "0x00ff00" if score > 80 else "0xffee00" if score > 50 else "0xff0000" },
                            emissiveIntensity: 0.5
                        }});
                        const torus = new THREE.Mesh(geometry, material);
                        scene.add(torus);
                        const light = new THREE.PointLight(0xffffff, 1, 100);
                        light.position.set(10, 10, 10);
                        scene.add(light);
                        scene.add(new THREE.AmbientLight(0x404040));
                        camera.position.z = 30;
                        function animate() {{ requestAnimationFrame(animate); torus.rotation.x += 0.01; torus.rotation.y += 0.01; renderer.render(scene, camera); }}
                        animate();
                    }})();
                </script>
                """
                html(gauge_html, height=300)
                st.markdown(f"<h1 style='text-align: center; color: white;'>{score}%</h1>", unsafe_allow_html=True)
                for sug in res['suggestions']: st.warning(sug)

    elif choice == "Export":
        st.markdown("### 📄 Preview & Export")
        from core.pdf_generator import PDFGenerator
        col_preview, col_download = st.columns([2, 1])
        with col_preview:
            resume_html_content = f"""
                <div style="font-family: Arial; padding: 20px; color: #333;">
                    <h1 style="text-align: center;">{st.session_state.resume_data.full_name}</h1>
                    <p style="text-align: center; font-size: 12px;">{st.session_state.resume_data.email} | {st.session_state.resume_data.phone}</p>
                    <hr>
                    <h3 style="color: #4b0082;">Summary</h3><p style="font-size: 13px;">{st.session_state.resume_data.summary}</p>
                    <h3 style="color: #4b0082;">Experience</h3>
                    <div style="font-size: 13px;">
                        {''.join([f"<b>{e.role} at {e.company}</b><br><ul style='margin-top:0;'>{''.join([f'<li>{b}</li>' for b in e.description])}</ul>" for e in st.session_state.resume_data.experience])}
                    </div>
                    <h3 style="color: #4b0082;">Skills</h3><p style="font-size: 13px;">{', '.join(st.session_state.resume_data.skills)}</p>
                </div>
            """
            card_html = f"""
            <div style="perspective: 1000px; display: flex; justify-content: center; align-items: center; height: 600px;">
                <div id="resume-card" style="width: 400px; height: 550px; background: white; border-radius: 15px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); transition: transform 0.1s ease-out; transform-style: preserve-3d; cursor: pointer; overflow: hidden;">
                    {resume_html_content}
                </div>
            </div>
            <script>
                const card = document.getElementById('resume-card');
                document.addEventListener('mousemove', (e) => {{
                    const x = (window.innerWidth / 2 - e.pageX) / 25;
                    const y = (window.innerHeight / 2 - e.pageY) / 25;
                    card.style.transform = `rotateY(${{x}}deg) rotateX(${{-y}}deg)`;
                }});
                document.addEventListener('mouseleave', () => {{ card.style.transform = 'rotateY(0deg) rotateX(0deg)'; }});
            </script>
            """
            html(card_html, height=600)
        with col_download:
            if st.button("Generate PDF 📄"):
                gen = PDFGenerator()
                pdf_bytes = gen.build_pdf(st.session_state.resume_data)
                st.download_button("Download ATS-Safe PDF", pdf_bytes, f"{st.session_state.resume_data.full_name}.pdf", "application/pdf")

    elif choice == "Admin":
        st.markdown("### ⚙️ System Admin")
        st.info("Anonymous Session Monitoring")
        st.metric("Active Session ID", "RSN-8821-X")
        st.metric("AI Tokens Used (Est)", f"{st.session_state.token_usage} tokens")
        st.progress(0.1, text="API Latency: 140ms")

if __name__ == "__main__":
    main()
