import sys
import os
import socket
import json
import getpass
import time

import clientHelpers

ip = clientHelpers.getData('client_data/ip_servidor.txt')

HOST = ip
PORT = 10000  

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

path = '//home/'

uploadData = {
  "apelido": clientHelpers.getData('client_data/apelido_usuario.txt'),
  "nome_arquivo": "",
  "conteudo_arquivo": ""
}

downloadData = {
  "id": "",
  "apelido": clientHelpers.getData('client_data/apelido_usuario.txt'),
}

def toConnect():
  try:
    client.connect((HOST, PORT))
  except Exception as e: print("erro: ",e, '>>> Servidor pode esta fora do ar ou o endereco IP esta incorreto')

def showMenu():
  print('\nInforme uma das opcoes:\n')
  print('1. Transmitir arquivos'
      '\n2. Listar arquivos' 
      '\n3. Baixar arquivos'
      '\n4. Configuracoes'
      '\n5. Sair\n')
  
  option = int(input('>>> '))
  handleSelectedOption(option)

def handleSelectedOption(option):
  if (option != 5 and option != 4):
    if not clientHelpers.isEmpty('client_data/apelido_usuario.txt'):
      if not clientHelpers.isEmpty('client_data/diretorio_download.txt'):
        handleMenu(option) 
      else: 
        print('CONFIGURE UM DIRETORIO PARA DOWNLOAD PRIMEIRO\n')
    else:
      print('CONFIGURE UM APELIDO PRIMEIRO\n')
      
  elif (option == 5):
    print('Saindo...')

  else: 
    showSubMenu()

def handleMenu(option):
  try:
    toConnect()
    case = {
    1: lambda option: upload(),
    2: lambda option: toList(),
    3: lambda option: download(),
    }
    return case[option](option)

  except:
    print('ID errado ou Erro no Servidor\n')
    showMenu()

def upload():
  client.sendall(str.encode('TRANSMITIR')) 
  response = client.recv(1024)

  if response.decode() == '255':
    if len(path) >= 7:
      getUserName() 

    fileDirectory = input('\nInforme o diretorio do arquivo que deseja transmitir\nEx: ../Documentos/testando/teste.txt\n\n>>> '+path)
    while not os.path.exists(path+fileDirectory):
      fileDirectory = input('\nInsira um diretorio valido (lembre-se que os acentos contam)\n>>> '+path)

    with open(path+fileDirectory, 'r') as file:
      content = (file.read())

      uploadData['nome_arquivo'] = clientHelpers.getFileName(fileDirectory)
      uploadData['conteudo_arquivo'] = content

      data = json.dumps(uploadData)
      client.sendall(bytes(data, encoding="utf-8"))
      response = client.recv(1024);
      print('O ID do seu arquivo é:', response.decode())

  else: 
    print('Nao foi possivel se comunicar com o servidor')

def toList():
  client.sendall(str.encode('LISTAR'))
  response = client.recv(1024)
  if response.decode() == '255':
    data = json.dumps(uploadData['apelido'])

    client.sendall(bytes(data, encoding="utf-8"))

    response = client.recv(1024)
    print(response.decode())

def download():
  client.sendall(str.encode('BAIXAR'))
  response = client.recv(1024)
  if response.decode() == '255':
    fileId = input('\nInforme o ID do arquivo que deseja baixar:\n>>> ')

    downloadData['id'] = fileId

    data = json.dumps(downloadData)
    client.sendall(bytes(data, encoding="utf-8"))

    response = json.loads(client.recv(1024))
    downloadRoute = clientHelpers.getData('client_data/diretorio_download.txt')+response['nome_arquivo']

    with open(downloadRoute, 'w') as file:
      for value in response['conteudo']:
        file.write(value)
      file.close()
      print('\nARQUIVO BAIXADO COM SUCESSO! Rota: '+downloadRoute)
  
def updatePath(currentDirectory):
  global path
  path = path+currentDirectory+'/'

  return path

def getUserName():
  userName = getpass.getuser()
  updatePath(userName)

def showSubMenu():
  subMenuOption = int(input('\n1. Configurar apelido' 
                    '\n2. Configurar diretorio de download'
                    '\n3. Configurar endereço IP do Coordenador'
                    '\n4. Voltar'
                    '\n\n>>> '))
  
  handleSubMenu(subMenuOption)

def handleSubMenu(option):
  try:
    case = {
    1: lambda option: confNickName(),
    2: lambda option: confDownload(),
    3: lambda option: confIP(),
    4: lambda option: showMenu(),
    }
    return case[option](option)

  except:
    print('OPCAO INVALIDA!')
    showSubMenu()

def confNickName():
  apelido_usuario = input('Informe seu apelido: ')
  with open('client_data/apelido_usuario.txt','w') as arquivo:
    arquivo.write(apelido_usuario)
    print('Apelido configurado para: ', apelido_usuario)


def confDownload():
  getUserName()
  clientHelpers.listDirectory(path)

  directory = input('\n## Escolha um dos diretorios listados acima ##\nEx: Downloads\n>>> ')

  while not os.path.exists(path+directory):
    print('\nInsira um diretorio valido (lembre-se que os acentos contam)')
    directory = input('>>> ')

  with open('client_data/diretorio_download.txt','w') as arquivo:
    arquivo.write(path+directory+'/')
    print('\nSua rota de download foi configurada para: ' + path+directory)

def confIP():
  global ip
  ip = input('\n## Informe o IP do servidor ##\n>>> ')

  with open('client_data/ip_servidor.txt','w') as arquivo:
    arquivo.write(ip)
    print('\nIP do servidor configurado para: ' + ip)

showMenu()