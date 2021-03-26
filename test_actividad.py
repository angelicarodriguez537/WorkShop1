import unittest
import random

from src.modelo.declarative_base import Session, Base, declarative_base, engine
from src.modelo.actividad import Actividad
from src.modelo.gasto import Gasto
from src.modelo.viajero import Viajero
from src.logica.Logica_mock import Logica_mock
from faker import Faker



class tests_actividades(unittest.TestCase):



    def tearDown(self):

        self.session = Session()

        busqueda_gastos = self.session.query(Gasto).all()
        busqueda_viajeros = self.session.query(Viajero).all()
        busqueda_actividad = self.session.query(Actividad).all()

        for gasto in busqueda_gastos:
            self.session.delete(gasto)

        for viajero in busqueda_viajeros:
            self.session.delete(viajero)

        for actividad in busqueda_actividad:
            self.session.delete(actividad)

        self.session.commit()
        self.session.close()

    
    def test_visualizar_lista_actividades_vacia(self):
     
        consulta0 = self.cuentas_claras.dar_actividades()

        self.assertIsNone(consulta0)

    def test_visualizar_lista_actividades_una_actividad(self):
        nombre_actividad = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        consulta1 = self.cuentas_claras.dar_actividades()
        self.assertEqual(len(consulta1),1)
    
    def test_visualizar_lista_actividades_con_mas_de_una_actividad(self):
        nombre_actividad0 = self.data_factory.name()
        nombre_actividad1 = self.data_factory.name()
        nombre_actividad2 = self.data_factory.name()
        nombre_actividad3 = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad0)
        self.cuentas_claras.insertar_actividad(nombre_actividad1)
        self.cuentas_claras.insertar_actividad(nombre_actividad2)
        self.cuentas_claras.insertar_actividad(nombre_actividad3)

        consulta1 = self.cuentas_claras.dar_actividades()
        self.assertGreater(len(consulta1),1)

    def test_visualizar_lista_gastos_por_actividd_vacia(self):

        nombre_actividad = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        actividad_id = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first().id
        consulta1 =self.cuentas_claras.dar_gastos_actividad(actividad_id)
        self.assertIsNone(consulta1)

    def test_visualizar_lista_gastos_por_actividad_con_un_gasto(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.gasto = Gasto(concepto=self.data_factory.name(),
                            valor=self.data_factory.random_int(1, 100),
                            fecha=self.data_factory.text())

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)
        self.session.add(self.gasto)

        viajero = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero and Viajero.apellido ==
                                                     apellido_viajero).first()
        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()


        actividad.gastos = [self.gasto]
        viajero.gastos = [self.gasto]
        self.session.commit()


        self.cuentas_claras.asociar_viajero_a_actividad(viajero.id, actividad.id)

        consulta1 = self.cuentas_claras.dar_gastos_actividad(actividad.id)
        self.assertEqual(len(consulta1),1)

    def test_visualizar_lista_gastos_por_actividad_con_mas_de_un_gasto(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.first_name()
        apellido_viajero = self.data_factory.last_name()
        gasto1 = Gasto(concepto=self.data_factory.name(), valor=self.data_factory.random_int(1, 100), fecha=self.data_factory.text())
        gasto2 = Gasto(concepto=self.data_factory.name(), valor=self.data_factory.random_int(1, 100), fecha=self.data_factory.text())
        gasto3 = Gasto(concepto=self.data_factory.name(), valor=self.data_factory.random_int(1, 100), fecha=self.data_factory.text())

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)
        self.session.add(gasto1)
        self.session.add(gasto2)
        self.session.add(gasto3)

        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        viajero = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()
        actividad.gastos = [gasto1, gasto2, gasto3]
        viajero.gastos = [gasto1, gasto2, gasto3]
        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(viajero.id , actividad.id)
        consulta1 =self.cuentas_claras.dar_gastos_actividad(actividad.id)

        self.assertGreater(len(consulta1),1)


    def test_reporte_compensacion_actividad_sin_gastos(self):

       nombre_actividad = self.data_factory.name()

       self.cuentas_claras.insertar_actividad(nombre_actividad)

       actividad_id = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first().id

       matriz = self.cuentas_claras.generar_reporte_compensacion(actividad_id)


       total = 0
       for i in range(2,len(matriz)):

           for j in range(1,len(matriz[i])):
               if matriz[i][j]==-1:
                   pass
               else:
                  total = total + matriz[i][j]

       self.assertEqual(total, 0)

    def test_reporte_compensacion_actividad_con_un_gasto(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())

        self.actividad0 = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero0 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero
                                                           and Viajero.apellido == apellido_viajero).first()

        self.session.add(self.gasto1)

        self.actividad0.gastos = [self.gasto1]
        self.viajero0.gastos = [self.gasto1]

        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero0.id, self.actividad0.id)

        matriz = self.cuentas_claras.generar_reporte_compensacion(self.actividad0.id)

        total = 0
        for i in range(1,len(matriz)):

            for j in range(1,len(matriz[i])):
                if matriz[i][j]==-1:
                    pass
                else:
                    total = total + matriz[i][j]

        self.assertEqual(total, self.gasto1.valor)

    def test_reporte_compensacion_actividad_con_un_viajero_con_n_gastos(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto2 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto3 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto4 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())

        self.actividad0 = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero0 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero
                                                           and Viajero.apellido == apellido_viajero).first()

        self.session.add(self.gasto1)
        self.session.add(self.gasto2)
        self.session.add(self.gasto3)
        self.session.add(self.gasto4)

        self.actividad0.gastos = [self.gasto1, self.gasto2, self.gasto3, self.gasto4]
        self.viajero0.gastos = [self.gasto1, self.gasto2, self.gasto3,self.gasto4]

        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero0.id, self.actividad0.id)

        matriz = self.cuentas_claras.generar_reporte_compensacion(self.actividad0.id)

        total = 0
        for i in range(2, len(matriz)):

            for j in range(1, len(matriz[i])):
                total = total + matriz[i][j]

        self.assertEqual(total, -1)

    def test_reporte_compensacion_actividad_con_varios_viajeros_con_n_gastos_sin_compensacion(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.first_name()
        apellido_viajero = self.data_factory.last_name()
        nombre_viajero1 = self.data_factory.first_name()
        apellido_viajero1 = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)
        self.cuentas_claras.agregar_viajero(nombre_viajero1, apellido_viajero1)

        self.data_valores = [self.data_factory.random_int(1,1000) for i in range(4)]
        self.suma_valores = 0

        for  valor in self.data_valores:
            self.suma_valores+=valor

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_valores[0],
                       fecha=self.data_factory.date())
        self.gasto2 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_valores[1],
                       fecha=self.data_factory.date())
        self.gasto3 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_valores[2],
                       fecha=self.data_factory.date())
        self.gasto4 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_valores[3],
                       fecha=self.data_factory.date())
        self.gasto5 = Gasto(concepto=self.data_factory.name(),
                       valor=self.suma_valores,
                       fecha=self.data_factory.date())

        self.actividad0 = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero0 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero
                                                           and Viajero.apellido == apellido_viajero).first()
        self.viajero1 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero1
                                                           and Viajero.apellido == apellido_viajero1).first()

        self.session.add(self.gasto1)
        self.session.add(self.gasto2)
        self.session.add(self.gasto3)
        self.session.add(self.gasto4)
        self.session.add(self.gasto5)

        self.actividad0.gastos = [self.gasto1, self.gasto2, self.gasto3,self.gasto4,self.gasto5]
        self.viajero0.gastos = [self.gasto1, self.gasto2, self.gasto3,self.gasto4]
        self.viajero1.gastos = [self.gasto5]

        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero0.id, self.actividad0.id)
        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero1.id, self.actividad0.id)

        matriz = self.cuentas_claras.generar_reporte_compensacion(self.actividad0.id)

        valores_gastos = [gasto.valor for gasto in self.session.query(Gasto).filter(Gasto.actividad == self.actividad0.id).all()]

        total_valores=0
        for valor in valores_gastos:
            total_valores=total_valores+valor


        total = 0
        for i in range(2, len(matriz)):

            for j in range(1, len(matriz[i])):
                total = total + matriz[i][j]

        total_gastos = 0

        for j in range(1, len(matriz[1])):
            total_gastos =total_gastos+matriz[1][j]

        self.assertEqual(total, -2)
        self.assertEqual(total_gastos, total_valores)

    def test_reporte_compensacion_actividad_con_varios_viajeros_con_n_gastos_con_compensacion(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.first_name()
        apellido_viajero = self.data_factory.last_name()
        nombre_viajero1 = self.data_factory.first_name()
        apellido_viajero1 = self.data_factory.last_name()
        nombre_viajero2 = self.data_factory.first_name()
        apellido_viajero2 = self.data_factory.last_name()
        nombre_viajero3 = self.data_factory.first_name()
        apellido_viajero3 = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)
        self.cuentas_claras.agregar_viajero(nombre_viajero1, apellido_viajero1)
        self.cuentas_claras.agregar_viajero(nombre_viajero2, apellido_viajero2)
        self.cuentas_claras.agregar_viajero(nombre_viajero3, apellido_viajero3)

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto2 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto3 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto4 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto5 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto6 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto7 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())
        self.gasto8 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,1000),
                       fecha=self.data_factory.date())

        self.actividad0 = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero0 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero
                                                           and Viajero.apellido == apellido_viajero).first()
        self.viajero1 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero1
                                                           and Viajero.apellido == apellido_viajero1).first()
        self.viajero2 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero2
                                                           and Viajero.apellido == apellido_viajero2).first()
        self.viajero3 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero3
                                                           and Viajero.apellido == apellido_viajero3).first()

        self.session.add(self.gasto1)
        self.session.add(self.gasto2)
        self.session.add(self.gasto3)
        self.session.add(self.gasto4)
        self.session.add(self.gasto5)
        self.session.add(self.gasto6)
        self.session.add(self.gasto7)
        self.session.add(self.gasto8)

        self.actividad0.gastos = [self.gasto1, self.gasto2, self.gasto3,self.gasto4,self.gasto5, self.gasto6, self.gasto7, self.gasto8]
        self.viajero0.gastos = [self.gasto1, self.gasto2, self.gasto3,self.gasto4]
        self.viajero1.gastos = [self.gasto5,self.gasto6]
        self.viajero3.gastos =[self.gasto7, self.gasto8]

        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero0.id, self.actividad0.id)
        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero1.id, self.actividad0.id)
        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero2.id, self.actividad0.id)
        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero3.id, self.actividad0.id)

        matriz = self.cuentas_claras.generar_reporte_compensacion(self.actividad0.id)

        total_viajeros = len(self.session.query(Viajero).filter(Viajero.actividades.any(Actividad.id == self.actividad0.id)).all())

        valores_gastos = [gasto.valor for gasto in self.session.query(Gasto).filter(Gasto.actividad == self.actividad0.id).all()]

        total_valores=0
        for valor in valores_gastos:
            total_valores=total_valores+valor


        total = 0
        for i in range(2, len(matriz)):

            for j in range(1, len(matriz[i])):
                total = total + matriz[i][j]

        total_gastos = 0

        for j in range(1, len(matriz[1])):
            total_gastos =total_gastos+matriz[1][j]

        suma_columna=0
        for j in range(1,total_viajeros+1):
            for i in range(1, total_viajeros+2):
                if matriz[1][j] <= (total_valores/total_viajeros):
                    if matriz[i][j]==-1:
                        pass
                    else:
                        suma_columna=suma_columna+matriz[i][j]
                    if i == total_viajeros+1:
                        self.assertEqual(suma_columna,total_valores/total_viajeros)
                        suma_columna=0


        self.assertEqual(total_gastos, total_valores)

    def test_insertar_actividad(self):

        nombre_actividad1 = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad1)

        nombre_actividad2 = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad2)

        consulta1 = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad1).first()
        consulta2 = self.session.query(Actividad).filter(Actividad.id == 2).first()
        consulta3 = self.session.query(Actividad).all()

        self.assertEqual(consulta1.nombre, nombre_actividad1)
        self.assertEqual(consulta2.nombre, nombre_actividad2)
        self.assertEqual(len(consulta3), 2)


    def test_insertar_actividad_con_mismo_nombre(self):

        nombre_actividad1 = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad1)

        nombre_actividad2 = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad2)

        prueba_guardado = self.cuentas_claras.insertar_actividad(nombre_actividad1)


        consulta3 = self.session.query(Actividad).all()

        self.assertEqual(len(consulta3), 2)
        self.assertEqual(prueba_guardado, False)

    def test_asociar_un_viajero_a_una_actividad(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)

        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        viajero = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()

        resultado = self.cuentas_claras.asociar_viajero_a_actividad(viajero.id, actividad.id)

        viajeros_de_actividad = self.session.query(Viajero).filter(Viajero.actividades.any(Actividad.id == actividad.id)).all()

        self.assertEqual(resultado, True)
        self.assertGreater(len(viajeros_de_actividad),0)

    def test_asociar_viajero_repetido_a_una_actividad(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)


        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        viajero = self.session.query(Viajero).filter(
            Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()


        resultado1 = self.cuentas_claras.asociar_viajero_a_actividad(viajero.id, actividad.id)
        resultado2 = self.cuentas_claras.asociar_viajero_a_actividad(viajero.id, actividad.id)

        self.assertEqual(resultado1, True)
        self.assertEqual(resultado2, False)

    def test_asociar_viajero_a_actividad_inexistente(self):

        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)

        viajero = self.session.query(Viajero).filter(
            Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()

        resultado1 = self.cuentas_claras.asociar_viajero_a_actividad(viajero.id, 1)

        self.assertEqual(resultado1, False)

    def test_asociar_viajero_inexistente_a_actividad(self):

        nombre_actividad = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)

        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()

        resultado1 = self.cuentas_claras.asociar_viajero_a_actividad(1, actividad.id)

        self.assertEqual(resultado1, False)


    def test_asociar_n_viajeros_a_actividad(self):

        nombre_actividad = self.data_factory.name()

        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        nombre_viajero2 = self.data_factory.unique.first_name()
        apellido_viajero2 = self.data_factory.last_name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)
        self.cuentas_claras.agregar_viajero(nombre_viajero2, apellido_viajero2)

        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        viajero = self.session.query(Viajero).filter(
            Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()

        viajero2 = self.session.query(Viajero).filter(
            Viajero.nombre == nombre_viajero2 and Viajero.apellido == apellido_viajero2).first()

        resultado1 = self.cuentas_claras.asociar_viajero_a_actividad(viajero.id, actividad.id)
        resultado2 = self.cuentas_claras.asociar_viajero_a_actividad(viajero2.id, actividad.id)

        viajeros_de_actividad = self.session.query(Viajero).filter(
            Viajero.actividades.any(Actividad.id == actividad.id)).all()


        self.assertEqual(resultado1, True)
        self.assertEqual(resultado2, True)
        self.assertEqual(viajeros_de_actividad[0].nombre, viajero.nombre)
        self.assertEqual(viajeros_de_actividad[1].apellido, viajero2.apellido)

    def test_reporte_gastos_actividad_sin_gastos(self):

        nombre_actividad = self.data_factory.name()

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()

        matriz = self.cuentas_claras.reporte_gastos_viajero(actividad.id)

        self.assertEqual(len(matriz[0]),0)

    def test_reporte_gastos_actividad_con_un_gasto(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,100),
                       fecha=self.data_factory.text())

        self.session.add(self.gasto1)
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)

        self.actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()


        self.actividad.gastos =[self.gasto1]
        self.viajero.gastos =[self.gasto1]
        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero.id, self.actividad.id)

        matriz = self.cuentas_claras.reporte_gastos_viajero(self.actividad.id)



        total = 0

        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                if j == 1:
                    total = total + matriz[i][j]

        self.assertEqual(total,self.gasto1.valor)

    def test_reporte_n_gastos_con_un_viajero(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,100),
                       fecha=self.data_factory.text())
        self.gasto2 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,100),
                       fecha=self.data_factory.text())
        self.gasto3 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,500),
                       fecha=self.data_factory.text())
        self.gasto4 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,300),
                       fecha=self.data_factory.text())


        self.session.add(self.gasto1)
        self.session.add(self.gasto2)
        self.session.add(self.gasto3)
        self.session.add(self.gasto4)

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)

        self.actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()

        self.actividad.gastos =[self.gasto1, self.gasto2, self.gasto3,self.gasto4]
        self.viajero.gastos =[self.gasto1, self.gasto2, self.gasto3,self.gasto4]
        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero.id, self.actividad.id)

        matriz = self.cuentas_claras.reporte_gastos_viajero(self.actividad.id)



        total = 0

        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                if j == 1:
                    total = total + matriz[i][j]

        self.assertEqual(total,(self.gasto1.valor+self.gasto2.valor+self.gasto3.valor+self.gasto4.valor))
        self.assertEqual(len(matriz),1)

    def test_reporte_n_gastos_con_n_viajer(self):

        nombre_actividad = self.data_factory.name()
        nombre_viajero = self.data_factory.unique.first_name()
        apellido_viajero = self.data_factory.last_name()

        nombre_viajero2 = self.data_factory.unique.first_name()
        apellido_viajero2 = self.data_factory.last_name()

        nombre_viajero3 = self.data_factory.unique.first_name()
        apellido_viajero3 = self.data_factory.last_name()

        self.gasto1 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,100),
                       fecha=self.data_factory.text())
        self.gasto2 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,100),
                       fecha=self.data_factory.text())
        self.gasto3 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,500),
                       fecha=self.data_factory.text())
        self.gasto4 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,300),
                       fecha=self.data_factory.text())

        self.gasto5 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,300),
                       fecha=self.data_factory.text())

        self.gasto6 = Gasto(concepto=self.data_factory.name(),
                       valor=self.data_factory.random_int(1,300),
                       fecha=self.data_factory.text())

        self.session.add(self.gasto1)
        self.session.add(self.gasto2)
        self.session.add(self.gasto3)
        self.session.add(self.gasto4)
        self.session.add(self.gasto5)
        self.session.add(self.gasto6)

        self.cuentas_claras.insertar_actividad(nombre_actividad)
        self.cuentas_claras.agregar_viajero(nombre_viajero, apellido_viajero)
        self.cuentas_claras.agregar_viajero(nombre_viajero2, apellido_viajero2)
        self.cuentas_claras.agregar_viajero(nombre_viajero3, apellido_viajero3)

        self.actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        self.viajero = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero and Viajero.apellido == apellido_viajero).first()
        self.viajero2 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero2 and Viajero.apellido == apellido_viajero2).first()
        self.viajero3 = self.session.query(Viajero).filter(Viajero.nombre == nombre_viajero3 and Viajero.apellido == apellido_viajero3).first()

        self.actividad.gastos =[self.gasto1, self.gasto2, self.gasto3,self.gasto4,self.gasto5,self.gasto6]
        self.viajero.gastos =[self.gasto1, self.gasto2, self.gasto3,self.gasto4]
        self.viajero2.gastos = [self.gasto5, self.gasto6]
        self.session.commit()

        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero.id, self.actividad.id)
        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero2.id, self.actividad.id)
        self.cuentas_claras.asociar_viajero_a_actividad(self.viajero3.id, self.actividad.id)


        matriz = self.cuentas_claras.reporte_gastos_viajero(self.actividad.id)
        gastos = [gasto.valor for gasto in self.session.query(Gasto).filter(Gasto.actividad ==self.actividad.id).all()]
        total_gastos=0
        for gasto in gastos:
            total_gastos =total_gastos+gasto

        total = 0

        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                if j == 1:
                    total = total + matriz[i][j]

        self.assertEqual(total,total_gastos)
        self.assertEqual(len(matriz),len(self.session.query(Viajero).filter(Viajero.actividades.any(Actividad.id == self.actividad.id)).all()))

    def test_editar_actividad(self):
        nombre_actividad = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        nuevo_nombre_actividad = self.data_factory.name()
        actividad_id = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first().id
        resultado = self.cuentas_claras.editar_actividad(nombre_actividad, nuevo_nombre_actividad)
        actividad = self.session.query(Actividad).filter(Actividad.id == actividad_id).first()
        self.assertEqual(resultado, True)
        self.assertEqual(actividad.nombre, nuevo_nombre_actividad)

    def test_editar_actividad_con_nombre_vacio(self):
        nombre_actividad = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        actividad_id = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first().id
        resultado = self.cuentas_claras.editar_actividad(nombre_actividad, " ")
        actividad = self.session.query(Actividad).filter(Actividad.id == actividad_id).first()
        self.assertEqual(resultado, False)
        self.assertEqual(actividad.nombre, nombre_actividad)

    def test_editar_actividad_con_campo_vacio(self):
        nombre_actividad = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        actividad_id = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first().id
        resultado = self.cuentas_claras.editar_actividad(nombre_actividad, None)
        actividad = self.session.query(Actividad).filter(Actividad.id == actividad_id).first()
        self.assertEqual(resultado, False)
        self.assertEqual(actividad.nombre, nombre_actividad)

    def test_editar_actividad_con_nombre_existente(self):
        nombre_actividad = self.data_factory.name()
        nombre_actividad2 = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad2)
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        nuevo_nombre_actividad = nombre_actividad2
        actividad_id = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first().id
        resultado = self.cuentas_claras.editar_actividad(nombre_actividad, nuevo_nombre_actividad)
        actividad = self.session.query(Actividad).filter(Actividad.id == actividad_id).first()
        self.assertEqual(resultado, False)
        self.assertEqual(actividad.nombre, nombre_actividad)

    def test_eliminar_actividad (self):
        nombre_actividad = self.data_factory.name()
        self.cuentas_claras.insertar_actividad(nombre_actividad)
        actividad = self.session.query(Actividad).filter(Actividad.nombre == nombre_actividad).first()
        resultado = self.cuentas_claras.eliminar_actividad(actividad.id)
        consulta = self.session.query(Actividad).filter(Actividad.id == actividad.id).first()
        self.assertEqual(resultado, True)
        self.assertIsNone(consulta)

    def test_eliminar_actividad_inexistente(self):
        resultado = self.cuentas_claras.eliminar_actividad(1)
        self.assertEqual(resultado, False)






















