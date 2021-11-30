# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import csv
import re


user_cuit = "cuit"
user_password = "password"
out_file_name = 'datosss.csv'
id_start = 54247
id_finish = 54250


class SigsaSpider(scrapy.Spider):
    name = 'sigsa'
    auth_data = {}
    allowed_domains = [
        'auth.afip.gob.ar',
        'www.afip.gob.ar',
        'aps2.senasa.gov.ar',
        'portalcf.cloud.afip.gob.ar',
    ]
    start_urls = ['https://auth.afip.gob.ar/contribuyente_/login.xhtml']

    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def parse(self, response):
        self.driver.get(self.start_urls[0])
        element = self.driver.find_element_by_id("F1:username")
        element.send_keys(user_cuit)
        self.driver.find_element_by_id("F1:btnSiguiente").click()
        element = WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.ID, "F1:password")))

        element.send_keys(user_password)
        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.ID, "F1:btnIngresar"))).click()

        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//div[@title='senasa_sigsa']"))).click()
        time.sleep(3)

        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])

        el = WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.NAME, "formulario:j_id4")))
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Venéreas - Fiscalizador':
                option.click()
                break
        el = self.driver.find_element_by_name("formulario:j_id28")
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Programa Venéreas':
                option.click()
                break
        self.driver.find_element_by_name("formulario:j_id35").click()

        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//a[@ng-show='menu.RASPAJES']"))).click()
        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//a[@ng-href='#/raspajes']"))).click()

        self.buscar()

        with open(out_file_name, 'a+', newline='') as file:
            writer = csv.writer(file)
            self.procesar_opciones(writer)

    def buscar(self):
        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.ID, "btnBuscar"))).click()

        el = WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//select[@ng-model='criteria.estado']")))
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Completada':
                option.click() # select() in earlier versions of webdriver
                break
        self.driver.find_element_by_xpath("//input[@ng-model='criteria.conPositivos']").click()
        self.driver.find_element_by_xpath("//button[@ng-click='find()']").click()

    def procesar_opciones(self, writer):
        for i in range(id_start, id_finish):
            self.driver.get("https://aps2.senasa.gov.ar/venereas/app/index.html#/planillaLaboratorio/" + str(i))

            time.sleep(1)
            WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'uneditable-input')][1]")))
            datos = self.driver.find_elements_by_xpath("//span[contains(@class,'uneditable-input')]")
            numero = datos[0].text
            estado = datos[1].text
            fecha_raspaje = datos[2].text
            metodo_raspaje = datos[3].text
            stock_toros = datos[4].text
            unidad_productiva = datos[5].text
            titular = datos[6].text
            fecha_recepcion = datos[7].text
            instalaciones = datos[8].text
            numero_protocolo = datos[9].text
            laboratorio = datos[10].text
            print('numero' + str(numero))
            print('estado' + str(estado))
            print('fecha_raspaje' + str(fecha_raspaje))
            print('metodo_raspaje' + str(metodo_raspaje))
            print('stock_toros' + str(stock_toros))
            print('unidad_productiva' + str(unidad_productiva))
            print('titular' + str(titular))
            print('fecha_recepcion' + str(fecha_recepcion))
            print('instalaciones' + str(instalaciones))
            print('numero_protocolo' + str(numero_protocolo))
            print('laboratorio' + str(laboratorio))

            datos_tabla = self.driver.find_element_by_xpath("//div[@class='span11']").text
            valores_campos_tabla = re.split(r'\s{2,}', datos_tabla)
            valores_campos_tabla = valores_campos_tabla[0].split('\n')
            print(valores_campos_tabla)
            valores_campos_tabla.pop(0)

            if "Anulada" in estado:
                csv_line = [
                        numero, estado, fecha_raspaje, metodo_raspaje,
                        stock_toros, unidad_productiva, titular, fecha_recepcion,
                        instalaciones, numero_protocolo, laboratorio,
                        "", "", "", "", "", ""
                    ]
                writer.writerow(csv_line)
            for valor in valores_campos_tabla:
                valor_separado = valor.split()
                print(valor_separado)
                try:
                    csv_line = [
                        numero, estado, fecha_raspaje, metodo_raspaje,
                        stock_toros, unidad_productiva, titular, fecha_recepcion,
                        instalaciones, numero_protocolo, laboratorio,
                        valor_separado[0], valor_separado[1], valor_separado[2], valor_separado[3], valor_separado[4], valor_separado[5]
                    ]
                    writer.writerow(csv_line)
                except Exception as exep:
                    valor_separado.insert(1, '')
                    csv_line = [
                        numero, estado, fecha_raspaje, metodo_raspaje,
                        stock_toros, unidad_productiva, titular, fecha_recepcion,
                        instalaciones, numero_protocolo, laboratorio,
                        valor_separado[0], valor_separado[1], valor_separado[2], valor_separado[3], valor_separado[4], valor_separado[5]
                    ]
                    writer.writerow(csv_line)
