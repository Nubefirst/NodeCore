# NodeCore Architecture

## Overview

NodeCore — это веб-платформа управления Linux-инфраструктурой.

На текущем этапе проект строится как модульный монолит.

Основная цель архитектуры — сохранить простоту разработки, четкое разделение ответственности и возможность дальнейшего расширения системы.

---

# Architectural Approach

## Modular Monolith

NodeCore использует архитектуру модульного монолита.

Все функциональные части системы находятся в одном backend-приложении, но разделены на независимые модули.

Основные преимущества:

- простота разработки;
- единое развертывание;
- понятная структура;
- возможность дальнейшего выделения отдельных сервисов при необходимости.

---

# High-Level Architecture

                Client

                  |

              Frontend

                  |

              REST API

                  |

          Backend Application

                  |
            Auth Users Monitoring Docker Audit
                              |

            Database Layer

                  |

            PostgreSQL

---

# Backend Structure

Backend разделен на несколько уровней:

Backend

├── API Layer

├── Application Layer

├── Domain Layer

├── Infrastructure Layer

└── Database Layer