# Projeto de Animação de Features do GOES-16

Este repositório contém os scripts e instruções necessários para gerar animações a partir das features extraídas dos dados do satélite GOES-16. A seguir, descrevemos os passos necessários para obter e processar os dados, bem como para gerar a animação final.

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Passo a Passo](#passo-a-passo)
  - [1. Obtenção dos Dados do GOES-16](#1-obtenção-dos-dados-do-goes-16)
  - [2. Extração das Features](#2-extração-das-features)
  - [3. Conversão para Formato Pickle](#3-conversão-para-formato-pickle)
  - [4. Geração da Animação](#4-geração-da-animação)
- [Exemplo de Execução](#exemplo-de-execução)
- [Contato](#contato)

## Pré-requisitos

Antes de iniciar, certifique-se de ter os seguintes pré-requisitos instalados em seu sistema:

- [Python 3.8+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- Bibliotecas Python necessárias:
  - `netCDF4`
  - `pickle`
  - `matplotlib` ou outra biblioteca para geração de animações

Você pode instalar as bibliotecas necessárias usando o seguinte comando:

```bash
pip install netCDF4 matplotlib
