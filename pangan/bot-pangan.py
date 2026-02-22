import asyncio
import os
import json
from playwright.async_api import async_playwright

async def main():
    try:
        with open('data_pangan.json') as f:
            data_klien = json.load(f)
    except FileNotFoundError:
        print("Error: File 'data_pangan.json' tidak ditemukan!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        for i, klien in enumerate(data_klien):
            print(f"[*] Meluncur! Memproses: {klien.get('nama')}")
            await page.goto("https://antrianpanganbersubsidi.pasarjaya.co.id/")

            # --- JURUS ANTI-GHAIB (Monitoring Tombol Tiap Detik) ---
            await page.evaluate("""() => {
                setInterval(() => {
                    // 1. Bersihkan modal penghalang
                    const modal = document.getElementById('blokirModal');
                    if(modal) modal.remove();
                    const backdrop = document.querySelector('.modal-backdrop');
                    if(backdrop) backdrop.remove();
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = 'auto';

                    // 2. Hancurkan style display:none
                    const styles = document.querySelectorAll('style');
                    styles.forEach(s => {
                        if(s.innerHTML.includes('submit')) s.remove();
                    });

                    // 3. Paksa Tombol Asli Muncul & Berwarna Mencolok
                    const btn = document.querySelector('button[type="submit"]');
                    if(btn) {
                        btn.style.setProperty('display', 'block', 'important');
                        btn.style.setProperty('visibility', 'visible', 'important');
                        btn.style.setProperty('opacity', '1', 'important');
                        btn.style.setProperty('background-color', '#ff0000', 'important'); // Merah
                        btn.style.setProperty('color', '#ffffff', 'important');
                        btn.innerHTML = 'GAS SIMPAN (KLIK SINI!)';
                        btn.disabled = false;
                    }
                }, 500); // Cek setiap 0.5 detik
            }""")

            # 3. ISI WILAYAH & TOKO (TURBO)
            await page.select_option('#wil', klien['wilayah'])
            await page.click('.select2-selection--single')
            await page.type('.select2-search__field', klien['keyword_toko'], delay=20)
            await asyncio.sleep(0.8) 
            await page.keyboard.press("Enter")

            # 4. ISI DATA (FLASH)
            await page.type('#kk', klien['kk'], delay=10)
            await page.type('#nik', klien['nik'], delay=10)
            await page.type('#kartu', klien['kartu'], delay=10)
            
            # Injection Tanggal Lahir
            tgl = klien['tgl_lahir']
            await page.evaluate(f'document.getElementById("tgllahir").value = "{tgl}"')
            await page.check('#dis')

            # 5. CAPTCHA
            try:
                captcha_img = await page.wait_for_selector('#captcha-img', timeout=3000)
                path_foto = os.path.abspath(f"temp_captcha_{i}.png")
                await captcha_img.screenshot(path=path_foto)
                os.startfile(path_foto) 
                await page.focus('#captha')
            except:
                print("[!] Captcha belum muncul.")

            print(f"[+] Klien {i+1}: CEK SEKARANG! Tombol MERAH harusnya muncul terus.")

            # 6. TUNGGU MANUVAL
            try: await asyncio.sleep(60)
            except: pass

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())