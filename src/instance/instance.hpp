#pragma once

#define NSBRKGA_MULTIPLE_INCLUSIONS

#include "nsbrkga.hpp"
#include <istream>
#include <ostream>
#include <vector>
#include <string>

namespace bmcp
{
    /***************************************************
     * The Instance class represents an instance of the
     * Balanced Multiway Cut Problem (Biobjective).
     ***************************************************/
    class Instance
    {
    public:
        /****************************
         * The number of objectives.
         ****************************/
        unsigned num_objectives;

        /*********************************
         * The optimization senses.
         *********************************/
        std::vector<NSBRKGA::Sense> senses;

        /********************************
         * This instance primal bounds.
         ********************************/
        std::vector<double> primal_bound;

        /**************************
         * The number of vertices.
         **************************/
        unsigned num_nodes;

        /**************************
         * The number of edges.
         **************************/
        unsigned num_edges;

        /**************************
         * The number of terminals.
         **************************/
        unsigned num_terminals;

        /**************************
         * Accumulated sum of edges cost.
         **************************/
        unsigned cumulative_edge_cost;

        /**************************
         * Representation of edges (the source node is represented by the adjacency list index where the arc e is).
         **************************/
        typedef struct
        {
            unsigned dst;
            unsigned cost;
        } edge;

        /**************************
         * Graph in adjascency list representation.
         **************************/
        std::vector<std::vector<edge>> G;

        /**************************
         * Terminal set S
         **************************/
        std::vector<unsigned> terminals;

         /**************************
         * is_terminal[t] = true for t in terminals
         **************************/
        std::vector<bool> is_terminal;

    private:
        /******************************
         * Initializes a new instance.
         ******************************/
        void init();

    public:
        /********************************
         * Constructs an empty instance.
         ********************************/
        Instance();

        /***********************************************************
         * Verifies whether this instance is valid.
         * @return true if this instance is valid; false otherwise.
         ***********************************************************/
        bool is_valid() const;


        // returns the position where the arc (i,j) is in the adjacency list of i or returns -1 if the arc does not exist.
        int get_edge_index(unsigned u, unsigned v) const;

        /**************************************************************************
         * Standard input operator.
         **************************************************************************/
        friend std::istream &operator>>(std::istream &is, Instance &instance);

        /*************************************************************
         * Standard output operator.
         *************************************************************/
        friend std::ostream &operator<<(std::ostream &os,
                                        const Instance &instance);
    };

}
