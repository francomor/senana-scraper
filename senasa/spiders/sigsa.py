# -*- coding: utf-8 -*-
import logging
import scrapy
from scrapy.selector import Selector
import json
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import csv
import re

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
        self.driver = webdriver.Chrome()

    def parse(self, response):
        self.driver.get(self.start_urls[0])
        element = self.driver.find_element_by_id("F1:username")
        element.send_keys("cuit")
        self.driver.find_element_by_id("F1:btnSiguiente").click()
        element = WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.ID, "F1:password")))

        element.send_keys("Jorgeafip18")
        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.ID, "F1:btnIngresar"))).click()

        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//div[@title='senasa_sigsa']"))).click()
        time.sleep(3)

        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])

        el = WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.NAME, "formulario:j_id4")))
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Venéreas - Fiscalizador':
                option.click() # select() in earlier versions of webdriver
                break
        el = self.driver.find_element_by_name("formulario:j_id27")
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Programa Venéreas':
                option.click() # select() in earlier versions of webdriver
                break
        self.driver.find_element_by_name("formulario:j_id33").click()

        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//a[@ng-show='menu.RASPAJES']"))).click()
        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//a[@ng-href='#/raspajes']"))).click()

        self.buscar()

        count_next = 0
        while 1:
            with open('datosss' + str(count_next) + '.csv', 'a+', newline='') as file:
                writer = csv.writer(file)
                # csv_line = [
                #     'numero', 'estado', 'fecha_raspaje', 'metodo_raspaje',
                #     'stock_toros', 'unidad_productiva', 'titular', 'fecha_recepcion',
                #     'instalaciones', 'numero_protocolo', 'laboratorio',
                #     'Caravana', 'Tubo', 'Número', 'Analizada', 'Campilobacter', 'Tricomona'
                # ]
                # writer.writerow(csv_line)
                self.procesar_opciones(writer, count_next)
            count_next += 1

    def procesar_opciones(self, writer, count_next):
        for i in range(38902, 50000):
            # WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='100']"))).click()
            #
            # for j_next in range(count_next):
            #     time.sleep(1)
            #     WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//button[@ng-click='next()']"))).click()
            #
            # WebDriverWait(self.driver, 600).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'Opciones')][1]")))
            # opciones_a_pasar = self.driver.find_elements_by_xpath("//a[contains(text(),'Opciones')]")
            # WebDriverWait(self.driver, 600).until(EC.presence_of_all_elements_located((By.XPATH, "//a[text()='Consultar planilla de laboratorio'][1]")))
            # elementos_a_pasar = self.driver.find_elements_by_xpath("//a[text()='Consultar planilla de laboratorio']")
            # opciones_a_pasar[i].click()
            #
            # elem = elementos_a_pasar[i]
            # actions = ActionChains(self.driver)
            # actions.move_to_element(elem).perform()
            # elem.send_keys(Keys.CONTROL + 't')
            # # elem.click()
            # windows = self.driver.window_handles
            # self.driver.switch_to.window(windows[2])

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

            # time.sleep(2)
            # self.driver.execute_script("window.history.go(-1)")
            # WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='close()']"))).click()

            # self.driver.close()
            # self.driver.switch_to.window(windows[2])
            # self.buscar()

    def buscar(self):
        WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.ID, "btnBuscar"))).click()

        el = WebDriverWait(self.driver, 600).until(EC.element_to_be_clickable((By.XPATH, "//select[@ng-model='criteria.estado']")))
        for option in el.find_elements_by_tag_name('option'):
            if option.text == 'Completada':
                option.click() # select() in earlier versions of webdriver
                break
        self.driver.find_element_by_xpath("//input[@ng-model='criteria.conPositivos']").click()
        self.driver.find_element_by_xpath("//button[@ng-click='find()']").click()

    # def parse(self, response):
    #     return scrapy.FormRequest.from_response(
    #         response,
    #         formdata={'F1:username': 'cuit'},
    #         callback=self.to_password
    #     )
    #
    # def to_password(self, response):
    #     # print(response.text)
    #     if "CUIT/CUIL" in response.text:
    #         print("\n\nFAIL\n\n")
    #         self.logger.error("Login failed")
    #         return
    #     else:
    #         if "TU CLAVE" in response.text:
    #             print("\n\n CUIL SET \n\n")
    #             return scrapy.FormRequest.from_response(
    #                 response,
    #                 formdata={'F1:password': 'Jorgeafip18'},
    #                 callback=self.redirecter
    #             )
    #         else:
    #             print("\n\nFAIL\n\n")
    #             self.logger.error("Login failed")
    #             return
    #
    # def redirecter(self, response):
    #     # print(response.text)
    #     print("URL: " + response.request.url)
    #     if "portalcf.cloud.afip.gob.ar" in response.text:
    #         print("\n\n LOGIN IN - REDIRECTING \n\n")
    #         return scrapy.FormRequest.from_response(
    #             response,
    #             callback=self.logged_in
    #         )
    #     else:
    #         print("\n\nFAIL\n\n")
    #         self.logger.error("Login failed")
    #         return
    #
    # def logged_in(self, response):
    #     # print(response.text)
    #     print("URL: " + response.request.url)
    #     url = 'https://portalcf.cloud.afip.gob.ar/portal/api/servicios/cuit/servicio/senasa_sigsa/autorizacion'
    #     return scrapy.Request(url, method='GET', callback=self.getted_token)
    #
    # def getted_token(self, response):
    #     # print(response.text)
    #     print("URL: " + response.request.url)
    #     url = 'https://aps2.senasa.gov.ar/sigsa/afip/index.seam'
    #     self.auth_data = json.loads(response.text)
    #     # print(auth_data)
    #     # print(json.dumps(auth_data))
    #     # print('aa')
    #     return scrapy.Request(
    #         url,
    #         method='POST',
    #         body=response.text,
    #         headers={'Content-Type':'application/json'},
    #         callback=self.in_sigsa
    #     )
    #
    # def in_sigsa(self, response):
    #     # print(response.text)
    #     print("URL: " + response.request.url)
    #     if "Bienvenido a SIGSA" in response.text:
    #         print("\n\n IN SIGSA \n\n")
    #         url = 'https://aps2.senasa.gov.ar/venereas/app/index.html'
    #         data = {
    #             "formulario": 'formulario',
    #             "formulario:j_id4": 'FVE',
    #             "formulario:j_id27": 'VEN',
    #             "formulario:j_id33": 'Ingresar',
    #             "formulario:token": self.auth_data["token"],
    #             "formulario:sign": self.auth_data["sign"],
    #             "javax.faces.ViewState": 'j_id1',
    #         }
    #         return scrapy.Request(
    #             url,
    #             method='POST',
    #             body=json.dumps(data),
    #             headers={'Content-Type': 'application/json'},
    #             callback=self.adentro_de_sigsa
    #         )
    #     else:
    #         print("\n\nNOT IN SIGSA\n\n")
    #         return
    #
    # def adentro_de_sigsa(self, response):
    #     print(response.text)
    #     print("URL: " + response.request.url)
    #     if "VenereasApp" in response.text:
    #         print("\n\n En raspaje de venereas \n\n")
    #         self.driver.get(response.request.url)
    #
    #         return
    #     else:
    #         print("\n\nNOT IN En raspaje de venereas\n\n")
    #         return

