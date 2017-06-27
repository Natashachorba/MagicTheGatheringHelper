/*Program that handles a few magic the gathering functions, currently:
1. prints out the shareboard given a directory of decks
2. removes all duplicates of a card in a list (sorta)
3. prints an alphabetical list given a list of cards from deckbox
4. removes all cards that are in the sideboard from the mainboard or viceversa*/

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <map>
#include <dirent.h>
#include <sys/types.h>
#include <iomanip>

using namespace std;

int main(int argc, char *argv[]){
	
	string line;
	/*takes a directory of txt files. Each file is a decklist. creates a map of
	all the cards and then prints out the cards that are shared accross	multiple
	decks, along with which decks each is in (not including basic lands)*/
	if (argc==1){
		DIR *mydirectory;
		struct dirent *entry;
		mydirectory=opendir("decks");
		if (mydirectory){
			struct dirent *entry;
			map<string,vector<string> > shared, decks;
			while ((entry=readdir(mydirectory))){//for each file
				if (entry->d_type==DT_REG) {//if its a txt file
					string temp=entry->d_name;
					string filepath="decks/"+temp;
					ifstream infile(filepath.c_str());//open it
					if (!infile){
						cout<<"error!";
						return 0;
					}
					//step through each line and compare cards
					while (getline(infile,line)){
						if (shared.find(line)!=shared.end()){//if you find copy
							shared[line].push_back(temp);
							decks[temp].push_back(line);
						}
						else {//else it's the 1st occurrence, add it to shared
							vector<string> tempvec;
							tempvec.push_back(temp);
							shared.insert(pair<string, vector<string> >(line,
							tempvec));
						}
					}
					infile.close();
				}
			}
			closedir(mydirectory);
			//prints all the shared cards
			for (map<string,vector<string> >::iterator i=shared.begin();
			i!=shared.end();i++){
				if (i->second.size()>1){
					cout<<i->first;
					for (int j=0; j<i->second.size();j++){
						cout<<" #"<<i->second[j];
					}
					cout<<endl;
				}
			}
			//print a list for each deck of shareboard to shareboard.txt
			ofstream outfile("shareboard.txt");
			if (!outfile){
				cout<<"error!";
				return 0;
			}
			for (map<string,vector<string> >::iterator i=decks.begin();
			i!=decks.end();i++){
				outfile<<setw(20)<<i->first<<" ("<<i->second.size()<<")";
				for (int j=0; j<i->second.size();j++){
					outfile<<"\n\n"<<i->second[j];
				}
				outfile<<endl<<endl;
			}
			outfile.close();
		}
	}
	else {
		ifstream infile("list.txt");
		if (!infile){
			cout<<"error!";
			return 0;
		}
		ifstream sefile("list2.txt");
		if (!sefile){
			cout<<"error second!";
			return 0;
		}
		//takes list and reduces all numbers to 1
		else if (argc==2 && argv[1]=="reduce"){
			while (getline(infile,line)){
				istringstream thing(line);
				string curr;
				int first=0;
				while (thing>>curr){
					if (!first){
						cout<<"1x ";
					}else{
						cout<<curr<<" ";
					}
					first++;
				}
				cout<<endl;
			}
		}
		//takes a list from deckbox and prints out just the card names minus crap
		else if (argc==2 && argv[1]=="cost"){
			while (getline(infile,line)){
				istringstream thing(line);
				string curr;
				
				while (thing>>curr){//reads the line until it hits type of card
					if (curr=="Creature" || curr=="Instant" || curr=="Sorcery" 
					|| curr=="Enchantment"){
						break;
					}
					cout<<curr<<" ";
				}
				cout<<endl;
			}
		}
		/*takes 2 lists from tappedout, one of which is the main board other is
		the	side, removes sideboard cards from main or vice versa (depending on
		order)*/
		else if (argc==2 && argv[1]=="share"){
			map<string,int> mymap;
			
			while (getline(infile,line)){
				mymap[line]=0;
			}
			while (getline(sefile,line)){
				if (mymap.find(line)!=mymap.end()){
					mymap[line]=1;
				}
			}
			for (map<string,int>::iterator i=mymap.begin();i!=mymap.end();i++){
				if (i->second==0){
					cout<<i->first<<endl;
				}
			}
			sefile.close();
		}
		infile.close();
	}
}