import zipfile, sys, io, openpyxl, time, resource, os
out = sys.argv[1]; nrows = int(sys.argv[2])
# start from a tiny valid workbook, then replace sheet1 xml with a big repetitive one
wb = openpyxl.Workbook(); ws = wb.active; ws.append(['a','b','c','d','e']); ws.append([1,2,3,4,5])
b = io.BytesIO(); wb.save(b); b.seek(0)
zin = zipfile.ZipFile(b)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for item in zin.infolist():
        if item.filename == 'xl/worksheets/sheet1.xml':
            with z.open('xl/worksheets/sheet1.xml', 'w', force_zip64=True) as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>')
                f.write(b'<row r="1"><c r="A1" t="inlineStr"><is><t>a</t></is></c><c r="B1" t="inlineStr"><is><t>b</t></is></c></row>')
                row = b'<row><c><v>1</v></c><c><v>1</v></c><c><v>1</v></c><c><v>1</v></c><c><v>1</v></c></row>'
                chunk = row * 10000
                for i in range(nrows // 10000): f.write(chunk)
                f.write(b'</sheetData></worksheet>')
        else:
            z.writestr(item, zin.read(item.filename))
zi = zipfile.ZipFile(out).getinfo('xl/worksheets/sheet1.xml')
print(f'compressed {os.path.getsize(out)/1e6:.2f} MB, sheet xml uncompressed {zi.file_size/1e6:.1f} MB, ratio {zi.file_size/os.path.getsize(out):.0f}:1')
