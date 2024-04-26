import requests
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import re

class Prueba():
    def __init__(self, placa):
        self.placa = placa

    def Peticion(self):
        headers = {
            'Host': 'portal.barranquilla.gov.co:8181',
            'Sec-Ch-Ua': '"Chromium";v="123", "Not:A-Brand";v="8"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Priority': 'u=0, i',
            'Connection': 'close',
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(
            'https://portal.barranquilla.gov.co:8181/ConsultaEstadoCuenta/consultaPlaca',
            headers=headers,
            verify=False,)
        soup = BeautifulSoup(response.text, 'html.parser')
        input = soup.find('input', {'id': 'j_id1:javax.faces.ViewState:1'})['value']
        form = soup.find('form', {'id': 'j_idt11'})['action']
        cookies = response.cookies.get_dict()
        data = {
            'form': 'form',
            'form:hora': f'{self.placa}',
            'javax.faces.ViewState': input,
            'form:btnIngresar': 'form:btnIngresar',
        }
        response = requests.post(
            "https://portal.barranquilla.gov.co:8181"+form,
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def procesar_fila_comparendo(self,row):
        # Extraer las celdas de la fila
        td = row.find_all('td')
        
        # Verificar si hay celdas y si hay más de una
        if td and len(td) > 1:
            return {
                'NumeroComparendo': td[0].text,
                'IdDocumento': td[1].text,
                'FechaResolucion': td[2].text,
                'NumeroResolucion': td[3].text,
                'TipoSancion': td[4].text,
                'EstadoComparendo': td[5].text,
                'ValorMulta': td[6].text,
                'Interes': td[7].text,
                'Costas': td[8].text
            }
        else:
            return {'Comparendo': 'No hay comparendos'}
        
    def obtener_informacion(self,soup):
        ComparendosFisicos = {}
        ComparendosElectronicos = {}
        
        div_fisicos = soup.find('div', attrs={'id': 'form:tbl'})
        if div_fisicos:
            ComFisicos = div_fisicos.find('tbody').find_all('tr')
            ComparendosFisicos = {'ComparendoFisico': [self.procesar_fila_comparendo(row) for row in ComFisicos]}

        div_electronicos = soup.find('div', attrs={'id': 'form:tblelectronicos'})
        if div_electronicos:
            ComElectronicos = div_electronicos.find('tbody').find_all('tr')
            ComparendosElectronicos = {'ComparendoElectronico': [self.procesar_fila_comparendo(row) for row in ComElectronicos]}

        return ComparendosFisicos, ComparendosElectronicos
        
if __name__ == "__main__":
    placa = input('Ingrese la placa: ')
    ExpresionRegular = r'((^[a-zA-Z]{3}\d{3}|[SRsr]{1}\d{5}|[a-zA-Z]{3}\d{2}[a-zA-Z]{1})$)'
    if not re.match(ExpresionRegular, placa):
        print('Placa no valida')
    else:
        prueba = Prueba(placa=placa)
        Soup = prueba.Peticion()
        ComparendosFisicos, ComparendosElectronicos = prueba.obtener_informacion(Soup)
        print("Comparendos Físicos:")
        print(pd.DataFrame(ComparendosFisicos['ComparendoFisico']))

        # Imprimir el DataFrame ComparendosElectronicos['ComparendoElectronico']
        print("\nComparendos Electrónicos:")
        print(pd.DataFrame(ComparendosElectronicos['ComparendoElectronico']))
        with pd.ExcelWriter('data.xlsx') as writer:
            # Escribir el primer DataFrame en la primera hoja
            pd.DataFrame(ComparendosFisicos['ComparendoFisico']).to_excel(writer, sheet_name='Comparendos Fisicos', index=False)  
            # Escribir el segundo DataFrame en una hoja diferente
            pd.DataFrame(ComparendosElectronicos['ComparendoElectronico']).to_excel(writer, sheet_name='Comparendos Electronicos', index=False)
        
