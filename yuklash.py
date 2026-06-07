import sys
import os

# ============================================================
# EXE ichida ishlasa, Playwright brauzer yo'lini to'g'rilaydi
# ============================================================
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    browsers_path = os.path.join(base_dir, "browsers")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

import asyncio
from playwright.async_api import async_playwright

# ============================================================
# SOZLAMALAR — o'zgartirish kerak bo'lsa shu yerda o'zgartir
# ============================================================
URL      = 'https://jonibekodoo-trot-2-test-33172300.dev.odoo.com'
LOGIN    = 'admin'
PASSWORD = '123456'

def kutish(msg="Tayyor bo'lsa Enter bos..."):
    input(f"\n⏸️  {msg}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page    = await context.new_page()
        page.set_default_timeout(20000)

        # ── Login ──────────────────────────────────────────
        print("🌐 Saytga ulanmoqda...")
        await page.goto(f'{URL}/web/login', wait_until='load')
        await asyncio.sleep(2)

        login_input = await page.query_selector('input#login')
        if login_input:
            await page.fill('input#login', LOGIN)
            await page.fill('input#password', PASSWORD)
            await page.locator('.oe_login_buttons button').click()
            await asyncio.sleep(3)
            print("✅ Login muvaffaqiyatli")
        else:
            print("✅ Allaqachon login qilingan")

        # ── BOM ro'yxatiga o'tish ──────────────────────────
        await page.goto(f'{URL}/odoo/action-775', wait_until='load')
        await asyncio.sleep(2)

        await page.locator('.o_data_row').first.click()
        await asyncio.sleep(2)

        # ── 'Consumed in Operation' ustuni borligini tekshir ─
        op_col = await page.locator('td.o_data_cell[name="operation_id"]').count()
        if op_col == 0:
            kutish("'Consumed in Operation' column yoqib qo'y va Enter bos...")

        # ── Asosiy tsikl ───────────────────────────────────
        bom_count = 0
        while True:
            bom_count += 1
            try:
                pager = await page.text_content('.o_pager_value')
                print(f"📋 {pager}", end=" → ")
            except Exception:
                print(f"📋 #{bom_count}", end=" → ")

            await page.mouse.click(10, 10)
            await asyncio.sleep(0.2)

            op_cells = await page.locator('td.o_data_cell[name="operation_id"]').all()

            changed = False
            for idx in range(len(op_cells)):
                cells = await page.locator('td.o_data_cell[name="operation_id"]').all()
                if idx >= len(cells):
                    break

                await page.mouse.click(10, 10)
                await asyncio.sleep(0.1)
                await cells[idx].click(force=True)
                await asyncio.sleep(0.4)

                inp = page.locator(
                    'td[name="operation_id"].o_currently_editing input,'
                    ' .o_selected_row td[name="operation_id"] input'
                ).first

                try:
                    await inp.clear()
                    await inp.fill('Ishlab chiqarish')
                    await asyncio.sleep(0.4)
                    option = page.locator(
                        '.o-autocomplete--dropdown-menu a, .ui-autocomplete li a'
                    ).first
                    await option.click(timeout=2000)
                    changed = True
                    await asyncio.sleep(0.2)
                except Exception:
                    await page.keyboard.press('Escape')

            if changed:
                await page.mouse.click(10, 10)
                await asyncio.sleep(0.1)
                try:
                    await page.locator('button.o_form_button_save:visible').click(timeout=2000)
                    await asyncio.sleep(1)
                except Exception:
                    await page.keyboard.press('Control+s')
                    await asyncio.sleep(1)

            lines = len(op_cells)
            print(f"{lines} ta satr ✅")

            # ── Keyingi sahifaga o'tish ───────────────────
            try:
                await page.locator('.o_pager_next').click(timeout=2000)
                await asyncio.sleep(1)
            except Exception:
                print("\n🎉 Barcha BOM lar yangilandi! Tugadi.")
                break

        await browser.close()

# ============================================================
if __name__ == "__main__":
    asyncio.run(main())