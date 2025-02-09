package main

import (
	"html/template"
	"log"
	"net/http"
)

func home(w http.ResponseWriter, r *http.Request) {

	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}

	files := []string{
		"./ui/templates/layout.html",
		"./ui/templates/pages/home.html",
	}

	ts, err := template.ParseFiles(files...)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	err = ts.ExecuteTemplate(w, "layout", nil)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}

}

func resume(w http.ResponseWriter, r *http.Request) {

	files := []string{
		"./ui/templates/layout.html",
		"./ui/templates/pages/resume.html",
	}

	ts, err := template.ParseFiles(files...)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	err = ts.ExecuteTemplate(w, "layout", nil)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}

}

func projects(w http.ResponseWriter, r *http.Request) {

	files := []string{
		"./ui/templates/layout.html",
		"./ui/templates/pages/projects.html",
	}

	ts, err := template.ParseFiles(files...)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	err = ts.ExecuteTemplate(w, "layout", nil)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}

}

func projectRaylibSnake(w http.ResponseWriter, r *http.Request) {

	files := []string{
		"./ui/templates/layout.html",
		"./ui/templates/emscripten/content.html",
		"./ui/templates/emscripten/scripts.html",
		"./ui/templates/pages/projects/raylib-snake.html",
	}

	ts, err := template.ParseFiles(files...)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	err = ts.ExecuteTemplate(w, "layout", nil)
	if err != nil {
		log.Print(err.Error())
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}

}

func main() {

	mux := http.NewServeMux()

	mux.Handle("/static/", http.StripPrefix("/static", http.FileServer(http.Dir("./ui/static"))))

	mux.HandleFunc("/", home)
	mux.HandleFunc("/resume", resume)
	mux.HandleFunc("/projects", projects)
	mux.HandleFunc("/projects/raylib-snake", projectRaylibSnake)

	err := http.ListenAndServe("127.0.0.1:4000", mux)
	log.Fatal(err)
}
